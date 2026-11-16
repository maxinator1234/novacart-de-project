import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def get_warehouse_connection():
    """Establishes a connection to the Data Warehouse (Port 5433)."""
    user = os.getenv("DW_USER")
    password = os.getenv("DW_PASSWORD")
    host = "localhost"
    port = "5433"
    db = os.getenv("DW_DB")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    return engine


def load_bronze_tables() -> None:
    """Reads validated Parquet files and loads them into the warehouse bronze schema."""
    # Map each target warehouse table name to its Parquet source file
    tables_to_load = {
        "users": os.path.join("data", "raw", "users.parquet"),
        "products": os.path.join("data", "raw", "products.parquet"),
        "orders": os.path.join("data", "raw", "orders.parquet"),
        "logistics": os.path.join("data", "processed", "clean_logistics.parquet"),
    }

    # Connect to the Data Warehouse and create the 'bronze' schema idempotently
    try:
        engine = get_warehouse_connection()
        with engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze;"))
        print("Connected to Data Warehouse and verified 'bronze' schema.")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not connect to Data Warehouse: {e}")
        sys.exit(1)

    # Loop through each dataset and load it into bronze.<table_name>
    for table_name, file_path in tables_to_load.items():
        try:
            print(f"\nReading {file_path}...")
            df = pd.read_parquet(file_path)
        except FileNotFoundError:
            print(f"CRITICAL ERROR: {file_path} not found. Did Extract/Validate run?")
            sys.exit(1)

        try:
            print(f"Loading {len(df)} rows into bronze.{table_name}...")
            df.to_sql(
                name=table_name,
                con=engine,
                schema="bronze",
                if_exists="replace",
                index=False,
            )
            print(f"Success! Loaded bronze.{table_name}.")
        except Exception as e:
            print(f"CRITICAL ERROR loading bronze.{table_name}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    load_bronze_tables()