import httpx
from typing import Dict, Any
from fastapi import HTTPException
import os
from app.flight_services.adapters.bdfare_adapter import convert_to_bdfare_request
# Load API credentials from environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")


async def fetch_bdfare_flights(payload: dict) -> dict:
    """
    Fetch flights from BDFare API.
    """
    transformed_payload = convert_to_bdfare_request(payload)  # Transform payload
    url = f"{BDFARE_BASE_URL}/AirShopping"
    headers = {
        "X-API-KEY": BDFARE_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=transformed_payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"BDFare API Error: {response.text}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while calling BDFare API: {str(e)}"
        )

# import requests
# import os
# import logging
# from fastapi import HTTPException

# class BDFAREClient:
#     def __init__(self):
#         # Read environment variables
#         self.base_url = os.getenv("BDFARE_BASE_URL")
#         self.apikey = os.getenv("BDFARE_API_KEY")
#         self.token = None
        
#         # Ensure that the required environment variables are set
#         if not self.base_url or not self.apikey:
#             logging.error("BDFARE_BASE_URL or BDFARE_API_KEY is not set in the environment variables.")
#             raise HTTPException(status_code=500, detail="API configuration is missing")

#         logging.info("Initializing BDFAREClient")
#         self.authenticate()  # Call the authenticate method during initialization

#     def authenticate(self):
#         """
#         Authenticate with the BDFARE API to retrieve a token.
#         """
#         url = f"{self.base_url}/Authenticate"
#         headers = {"Content-Type": "application/json"}
#         data = {"apikey": self.apikey}

#         try:
#             logging.info("Attempting to authenticate with BDFARE")
#             logging.debug(f"Request headers: {headers}, Request body: {data}")
            
#             response = requests.post(url, headers=headers, json=data)
#             logging.debug(f"Response status: {response.status_code}, Response body: {response.text}")
            
#             response.raise_for_status()  # Raise HTTPError for bad responses
#             self.token = response.json().get("TokenId")
#             if not self.token:
#                 logging.error("TokenId not found in authentication response.")
#                 raise ValueError("TokenId not found in authentication response.")
#             logging.info(f"Authentication successful, token received: {self.token}")
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Authentication request failed: {e}. Response: {response.text}")
#             raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")
#         except ValueError as e:
#             logging.error(f"Authentication token parsing failed: {e}")
#             raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")

#     def get_balance(self):
#         """
#         Retrieve balance from the BDFARE API.
#         """
#         if not self.token:
#             logging.info("Token missing, re-authenticating.")
#             self.authenticate()

#         url = f"{self.base_url}/GetBalance"
#         headers = {
#             "Authorization": f"Bearer {self.token}",
#             "Content-Type": "application/json"
#         }
#         data = {"UserName": self.apikey}  # Confirm payload structure from API documentation

#         try:
#             logging.info("Requesting balance from BDFARE")
#             response = requests.post(url, headers=headers, json=data)
#             response.raise_for_status()  # Check for HTTP errors
#             logging.debug(f"Balance response: {response.json()}")  # Log full response for debugging
#             logging.info("Balance request successful")
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Failed to get balance: {e}")
#             raise HTTPException(status_code=500, detail=f"Failed to get balance: {e}")
