import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_warehouse_connection():
    """Establishes a connection to the Data Warehouse (Port 5433)."""
    user = os.getenv('DW_USER')
    password = os.getenv('DW_PASSWORD')
    host = 'localhost'
    port = '5433'  # Notice we are targeting the new container!
    db = os.getenv('DW_DB')
    
    # Create the SQLAlchemy engine
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    return engine

def load_users_to_warehouse():
    """Reads the users Parquet file and loads it into the Data Warehouse."""
    
    # 1. Define the path to the Bronze data
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, 'data', 'raw', 'users.parquet')
    
    # 2. Read the Parquet file
    try:
        print(f"Reading data from {file_path}...")
        df = pd.read_parquet(file_path)
    except FileNotFoundError:
        print("CRITICAL ERROR: Parquet file not found. Did the Extract phase run?")
        return
        
    # 3. Connect to the Data Warehouse
    engine = get_warehouse_connection()
    
    # 4. Load the data
    try:
        print("Loading data into the 'users' table in the Data Warehouse...")
        # 'if_exists="replace"' means if the table is already there, overwrite it.
        # 'index=False' prevents Pandas from writing the row numbers as a database column.
        df.to_sql('users', engine, if_exists='replace', index=False)
        print("Success! Data loaded successfully.")
    except Exception as e:
        print(f"Failed to load data: {e}")

if __name__ == "__main__":
    load_users_to_warehouse()