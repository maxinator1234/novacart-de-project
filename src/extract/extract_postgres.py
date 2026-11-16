import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
load_dotenv()

# 2. Get credentials securely
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB = os.getenv("POSTGRES_DB")
HOST = "localhost"
PORT = "5432"

# 3. Create the SQLAlchemy connection string
connection_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"


def extract_table(table_name: str) -> pd.DataFrame:
    """Connects to Postgres and extracts a table to a Pandas DataFrame."""
    try:
        engine = create_engine(connection_string)
        print(f"Connecting to extract '{table_name}'...")

        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, engine)

        print(f"Extracted {len(df)} rows from '{table_name}' table:")
        print(df.head())
        return df

    except Exception as e:
        print(f"CRITICAL ERROR extracting '{table_name}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    tables = ["users", "products", "orders"]
    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    for table in tables:
        df = extract_table(table)
        file_path = os.path.join(output_dir, f"{table}.parquet")
        df.to_parquet(file_path, index=False)
        print(f"Saved {file_path}\n{'-'*40}")