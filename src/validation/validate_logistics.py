import os
import sys
import pandas as pd
import pandera.pandas as pa


def validate_logistics_data() -> pd.DataFrame:
    """Validates raw logistics CSV, quarantining bad rows into a Dead Letter Queue."""
    raw_path = os.path.join("data", "raw", "logistics.csv")
    processed_dir = os.path.join("data", "processed")
    quarantine_dir = os.path.join("data", "quarantine")

    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(quarantine_dir, exist_ok=True)

    clean_path = os.path.join(processed_dir, "clean_logistics.parquet")
    quarantine_path = os.path.join(quarantine_dir, "bad_logistics.csv")

    print("Validating logistics data...")
    df = pd.read_csv(raw_path)

    schema = pa.DataFrameSchema({
        "order_id": pa.Column(int, nullable=False),
        "shipping_status": pa.Column(
            str,
            nullable=False,
            checks=pa.Check.isin(["Shipped", "In Transit", "Delivered", "Delayed"]),
        ),
        "estimated_delivery": pa.Column(str, nullable=False),
    })

    try:
        clean_df = schema.validate(df, lazy=True)
        clean_df.to_parquet(clean_path, index=False)
        print(f"Success! All {len(clean_df)} rows passed validation -> {clean_path}")
        return clean_df

    except pa.errors.SchemaErrors as e:
        # Extract row indices of malformed records
        bad_indices = e.failure_cases["index"].dropna().unique()

        # If no row index exists, a structural/column-level error occurred -> fail fast
        if len(bad_indices) == 0:
            print(f"\nCRITICAL SCHEMA FAILURE: {e}")
            sys.exit(1)

        bad_df = df.loc[df.index.isin(bad_indices)]
        clean_df = df.loc[~df.index.isin(bad_indices)]

        # Route bad records to Dead Letter Queue (DLQ)
        bad_df.to_csv(quarantine_path, index=False)
        print(f"WARNING: Quarantined {len(bad_df)} bad row(s) -> {quarantine_path}")

        # Fail fast if zero valid rows remain
        if clean_df.empty:
            print("CRITICAL PIPELINE FAILURE: 0 valid rows remained after validation!")
            sys.exit(1)

        clean_df.to_parquet(clean_path, index=False)
        print(f"Success! Saved {len(clean_df)} valid row(s) -> {clean_path}")
        return clean_df


if __name__ == "__main__":
    validate_logistics_data()