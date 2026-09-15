import os
import pandas as pd
import pandera.pandas as pa

def validate_logistics_data():
    """Reads the raw CSV and validates it against our Data Contract."""
    
    # 1. Load the raw data
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, 'data', 'raw', 'logistics.csv')
    df = pd.read_csv(file_path)
    
    print("Validating Data...")
    
    # 2. Define the Data Contract (Schema)
    schema = pa.DataFrameSchema({
        # RULE 1: order_id must be a float (Pandas reads NULL ints as floats) and cannot be null
        "order_id": pa.Column(int, nullable=False),
        
        # RULE 2: shipping_status must be a string (str). It cannot be null.
        "shipping_status":pa.Column(str, nullable=False, checks=pa.Check.isin(["Shipped", "In Transit", "Delivered", "Delayed"])),
        
        # RULE 3: estimated_delivery must be a string (str). It cannot be null.
        "estimated_delivery":pa.Column(str, nullable=False),
    })
    
    # 3. Apply the validation
    try:
        validated_df = schema.validate(df)
        print("Success! Data passed all validation checks.")
        return validated_df
    except pa.errors.SchemaError as e:
        print("\nCRITICAL PIPELINE FAILURE: Data Validation Failed!")
        print(f"Error Details: {e}")
        # In production, we would stop the pipeline here.
        return None

if __name__ == "__main__":
    validate_logistics_data()