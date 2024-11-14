import requests
import os
from fastapi import HTTPException

class BDFAREClient:
    def __init__(self):
        # Set base URL for the sandbox environment
        self.base_url = "https://bdf.centralindia.cloudapp.azure.com/api/enterprise"  
        # Retrieve the username and API key from environment variables
        self.username = os.getenv("BDFARE_USERNAME")
        self.apikey = os.getenv("BDFARE_APIKEY")
        self.token = self.authenticate()

    def authenticate(self):
        url = f"{self.base_url}/Authenticate"
        headers = {"Content-Type": "application/json"}
        data = {"apikey": self.apikey}

        try:
            # Sending authentication request
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for HTTP errors

            # Extract token from the response
            token = response.json().get("TokenId")
            if not token:
                raise ValueError("Authentication failed: Token not found.")
            return token
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_balance(self):
        url = f"{self.base_url}/GetBalance"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {"UserName": self.username}

        try:
            # Request balance information
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to get balance: {e}")

# Example usage
try:
    client = BDFAREClient()
    balance_info = client.get_balance()
    print(balance_info)
except HTTPException as e:
    print(f"Error: {e.detail}")
