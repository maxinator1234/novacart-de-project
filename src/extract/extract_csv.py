import os
import pandas as pd

def generate_mock_csv(file_path):
    """Simulates the logistics company dropping a file on our server."""
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    data = {
        "order_id": [1, 2, 3, 4],  # Intentionally added a NULL (None)
        "shipping_status": ["Delivered", "In Transit", "UNKNOWN_ERROR", "Shipped"],
        "estimated_delivery": ["2026-09-02", "2026-09-06", "2026-09-10", "2026-09-05"]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Mock file generated at: {file_path}")

def extract_logistics_data():
    """Extracts the CSV data dropped by the logistics company."""
    
    # We use os.path.join to handle Windows (\) vs Linux (/) slashes automatically!
    # This points to: novacart-de-project/data/raw/logistics.csv
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, 'data', 'raw', 'logistics.csv')
    
    # 1. Generate the file first so we have something to read
    generate_mock_csv(file_path)
    
    # 2. Extract it
    try:
        print(f"\nAttempting to read file: {file_path}")
        df = pd.read_csv(file_path)
        print("Success! Extracted CSV data:")
        print(df)
    except FileNotFoundError:
        print("ERROR: The logistics file was not found! Did the provider fail to send it?")

if __name__ == "__main__":
    extract_logistics_data()