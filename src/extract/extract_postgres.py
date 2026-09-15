import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
load_dotenv()

# 2. Get credentials securely
USER = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB = os.getenv('POSTGRES_DB')
HOST = 'localhost'
PORT = '5432'

# 3. Create the SQLAlchemy connection string
# Format: postgresql://username:password@host:port/database_name
connection_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

def extract_table(table_name):
    """Connects to Postgres and extracts a table to a Pandas DataFrame."""
    try:
        # Create database engine
        engine = create_engine(connection_string)
        print(f"Successfully connected to the database!")
        
        # Execute query
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, engine)
        
        print(f"\nExtracted {len(df)} rows from '{table_name}' table:")
        print(df.head())
        return df
        
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

if __name__ == "__main__":
    # Test the function by extracting the users table
    users_df = extract_table("orders")
    file_path = os.path.join("data", "raw", "users.parquet")

    users_df.to_parquet(file_path)