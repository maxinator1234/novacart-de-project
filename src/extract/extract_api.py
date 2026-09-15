import requests

def extract_payment_data():
    """Extracts payment data from the Payment Gateway API."""
    
    # This URL intentionally simulates a broken API server
    api_url = "https://fakestoreapi.com/carts/1"
    
    print(f"Connecting to API: {api_url}")
    
    # Send the GET request
    response = requests.get(api_url)
    
    # Print the raw status code we received
    print(f"Received Status Code: {response.status_code}")
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Success! Here is the data:")
        data = response.json()
        print(data)
    else:
        print("CRITICAL PIPELINE FAILURE: The API is down!")
        # In a real company, this would trigger an email/Slack alert

if __name__ == "__main__":
    extract_payment_data()