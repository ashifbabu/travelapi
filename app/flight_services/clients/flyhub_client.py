import httpx
from typing import Dict, Any
from fastapi import HTTPException
import os
import time
import json
import requests
import subprocess
import logging

# Setup logger
logger = logging.getLogger("flyhub_client")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Load API credentials from environment variables
FLYHUB_BASE_URL = os.getenv("FLYHUB_PRODUCTION_URL")
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")

# Cached token for FlyHub
cached_token = {"token": None, "expires_at": 0}


def get_flyhub_token() -> str:
    """
    Retrieve a valid token for FlyHub API. If the cached token is expired or missing,
    request a new one.

    Returns:
        str: A valid FlyHub token.

    Raises:
        HTTPException: If token retrieval fails.
    """
    global cached_token

    # Check if the cached token is still valid
    if cached_token["token"] and cached_token["expires_at"] > time.time():
        logger.info("Using cached FlyHub token.")
        return cached_token["token"]

    # Request a new token
    url = f"{FLYHUB_BASE_URL}/Authenticate"
    payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

    if not FLYHUB_BASE_URL or not FLYHUB_USERNAME or not FLYHUB_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Missing FlyHub API configuration. Ensure FLYHUB_BASE_URL, FLYHUB_USERNAME, and FLYHUB_API_KEY are set."
        )

    try:
        logger.info("Requesting new FlyHub token...")
        response = httpx.post(url, json=payload)

        if response.status_code == 200:
            token_data = response.json()
            cached_token["token"] = token_data["TokenId"]
            # Assume token validity is 1 hour (3600 seconds)
            cached_token["expires_at"] = time.time() + 3600
            logger.info("FlyHub token retrieved successfully.")
            return cached_token["token"]
        else:
            logger.error(f"FlyHub Authentication Failed: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"FlyHub Authentication Failed: {response.text}"
            )
    except httpx.RequestError as e:
        logger.error(f"Network error during FlyHub Authentication: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Network error during FlyHub Authentication: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during FlyHub Authentication: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during FlyHub Authentication: {str(e)}"
        )


async def fetch_flyhub_flights(payload: dict) -> dict:
    """
    Fetch flights from FlyHub API and log the request payload.
    """
    try:
        # Authenticate and get the token
        token = get_flyhub_token()  # Ensure valid token

        if not token:
            raise HTTPException(
                status_code=500, detail="FlyHub authentication failed. Token is None."
            )

        # FlyHub API endpoint
        url = f"{FLYHUB_BASE_URL}/AirSearch"

        # Headers with the token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Log the request payload
        logger.info(f"Sending request to FlyHub: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Payload: {payload}")

        # Make the API call
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        # Handle the response
        if response.status_code == 200:
            logger.info("FlyHub response received successfully.")
            return response.json()
        else:
            logger.error(
                f"FlyHub API Error: {response.status_code} - {response.text}"
            )
            raise HTTPException(
                status_code=response.status_code,
                detail=f"FlyHub API Error: {response.text}",
            )
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logger.exception("Unexpected error occurred while calling FlyHub API.")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )

def authenticate_flyhub():
    """
    Authenticate with FlyHub API using a fallback mechanism.
    """
    global cached_token
    url = f"{FLYHUB_BASE_URL}/Authenticate"
    payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

    try:
        logger.info("Authenticating with FlyHub using requests...")
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            token_data = response.json()
            cached_token["token"] = token_data["TokenId"]
            # Assume token validity is 1 hour
            cached_token["expires_at"] = time.time() + 3600
            logger.info("FlyHub token successfully retrieved.")
        else:
            logger.error(f"FlyHub Authentication Failed: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"FlyHub Authentication Failed: {response.text}"
            )
    except Exception as e:
        logger.error(f"Error during FlyHub authentication: {str(e)}")
        fallback_authenticate_flyhub(payload, url)


def fallback_authenticate_flyhub(payload: dict, url: str):
    """
    Fallback mechanism for FlyHub authentication using curl.

    Args:
        payload (dict): The authentication payload.
        url (str): The authentication URL.
    """
    logger.warning("Attempting FlyHub authentication using curl as fallback...")
    payload_json = json.dumps(payload)
    curl_command = [
        "curl",
        "-X", "POST",
        url,
        "-H", "Content-Type: application/json",
        "-d", payload_json
    ]
    result = subprocess.run(curl_command, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"FlyHub authentication fallback failed: {result.stderr}")
        raise HTTPException(
            status_code=500,
            detail=f"FlyHub authentication fallback failed: {result.stderr}"
        )
    try:
        token_data = json.loads(result.stdout)
        cached_token["token"] = token_data["TokenId"]
        cached_token["expires_at"] = time.time() + 3600
        logger.info("FlyHub token successfully retrieved using curl fallback.")
    except json.JSONDecodeError:
        logger.error(f"Failed to parse FlyHub authentication fallback response: {result.stdout}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse FlyHub authentication fallback response: {result.stdout}"
        )



# import requests
# import os
# import logging
# from fastapi import HTTPException

# class FlyhubClient:
#     def __init__(self):
#         self.base_url = "https://api.flyhub.com/api/v1"
#         self.username = os.getenv("FLYHUB_USERNAME")
#         self.apikey = os.getenv("FLYHUB_APIKEY")
#         self.token = self.authenticate()

# def authenticate(self):
#     # Ensure there are no extra quotes in the base URL or endpoint
#     url = f"{self.base_url}/Authenticate"
#     headers = {"Content-Type": "application/json"}
#     data = {"apikey": self.apikey}

#     try:
#         logging.info("Attempting to authenticate with BDFARE")
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()  # Will raise HTTPError for bad responses
#         logging.debug(f"Authentication response: {response.json()}")  # Log full response for debugging
#         self.token = response.json().get("TokenId")
#         if not self.token:
#             raise ValueError("Token not found in authentication response.")
#         logging.info(f"Authentication successful, token received: {self.token}")
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Authentication failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")
#     except ValueError as e:
#         logging.error(f"Authentication failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")

#     def get_balance(self):
#         url = f"{self.base_url}/GetBalance"
#         headers = {
#             "Authorization": f"Bearer {self.token}",
#             "Content-Type": "application/json"
#         }
#         data = {"UserName": self.username}
#         response = requests.post(url, headers=headers, json=data)
#         return response.json() if response.status_code == 200 else response.json()
