#app\flight_services\clients\flyhub_client.py
import httpx
import json
import subprocess
from typing import Dict
from fastapi import HTTPException
import os
import logging
import time
import requests
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()

# Load API credentials from environment variables
FLYHUB_BASE_URL = os.getenv("FLYHUB_PRODUCTION_URL")
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")

# Logger setup
logger = logging.getLogger("flyhub_client")
logger.setLevel(logging.INFO)

# Example usage
if not FLYHUB_BASE_URL or not FLYHUB_USERNAME or not FLYHUB_API_KEY:
    logger.error("Missing required environment variables for FlyHub API.")
else:
    logger.info("FlyHub environment variables loaded successfully.")


# Cached token for FlyHub
cached_token = {"token": None, "expires_at": 0}


def validate_url(url: str):
    """Validate the FlyHub Base URL to ensure it includes a valid protocol."""
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(
            status_code=500,
            detail=f"Invalid FlyHub Base URL: {url}. Ensure it starts with 'http://' or 'https://'.",
        )


def get_flyhub_token() -> str:
    """
    Retrieve a valid token for FlyHub API.
    """
    global cached_token

    # Validate the FlyHub Base URL
    validate_url(FLYHUB_BASE_URL)

    # Check if the cached token is still valid
    if cached_token["token"] and cached_token["expires_at"] > time.time():
        return cached_token["token"]

    # Request a new token
    url = f"{FLYHUB_BASE_URL}/Authenticate"
    payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

    try:
        response = httpx.post(url, json=payload)
        if response.status_code == 200:
            token_data = response.json()
            cached_token["token"] = token_data["TokenId"]
            # Assume token validity is 1 hour (3600 seconds)
            cached_token["expires_at"] = time.time() + 3600
            logger.info("FlyHub token retrieved successfully.")
            return cached_token["token"]
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"FlyHub Authentication Failed: {response.text}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during FlyHub Authentication: {str(e)}",
        )
#updated
async def fetch_flyhub_ticket_cancel(payload: dict) -> dict:
    url = f"{FLYHUB_BASE_URL}/AirCancel"
    headers = {"Authorization": f"Bearer {get_flyhub_token()}", "Content-Type": "application/json"}

    logger.info(f"Sending Ticket Cancel request to FlyHub: {url}")
    logger.debug(f"Payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
        logger.info(f"FlyHub Ticket Cancel Response Status: {response.status_code}")
        logger.debug(f"FlyHub Ticket Cancel Response Body: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception("Error during FlyHub Ticket Cancel.")
        raise HTTPException(status_code=500, detail=f"Error in FlyHub Ticket Cancel: {str(e)}")

async def fetch_flyhub_ticket_issue(payload: dict) -> dict:
    """
    Fetch ticket issue details from FlyHub API.
    """
    url = f"{FLYHUB_BASE_URL}/AirTicketing"
    headers = {"Authorization": f"Bearer {get_flyhub_token()}", "Content-Type": "application/json"}

    logger.info(f"Sending Ticket Issue request to FlyHub: {url}")
    logger.debug(f"Payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
        logger.info(f"FlyHub Ticket Issue Response Status: {response.status_code}")
        logger.debug(f"FlyHub Ticket Issue Response Body: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception("Error during FlyHub Ticket Issue.")
        raise HTTPException(status_code=500, detail=f"Error in FlyHub Ticket Issue: {str(e)}")

async def fetch_flyhub_airretrieve(payload: dict) -> dict:
    """
    Fetch air retrieve details from FlyHub API.

    Args:
        payload (dict): Request payload with `BookingID`.

    Returns:
        dict: The response from the FlyHub API.

    Raises:
        HTTPException: If the request fails or an error occurs.
    """
    try:
        # Get a valid token (from cache or authenticate)
        token = get_flyhub_token()
        if not token:
            raise HTTPException(
                status_code=500,
                detail="FlyHub authentication failed. Token is None."
            )
        
        # Set up the API endpoint and headers
        url = f"{FLYHUB_BASE_URL}/AirRetrieve"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        # Log the request
        logger.info(f"Sending AirRetrieve request to FlyHub. URL: {url}")
        logger.info(f"Payload: {payload}")
        
        # Make the HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        
        # Raise for status if response indicates an error
        response.raise_for_status()
        
        # Log the response
        logger.info(f"FlyHub AirRetrieve response: {response.json()}")
        return response.json()

    except httpx.HTTPStatusError as http_err:
        logger.error(f"FlyHub API returned an HTTP error: {http_err.response.text}")
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"FlyHub API Error: {http_err.response.text}"
        )

    except Exception as e:
        logger.exception(f"Unexpected error occurred while fetching FlyHub AirRetrieve: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while fetching FlyHub AirRetrieve: {str(e)}"
        )

async def fetch_flyhub_airbook(search_id: str, result_id: str, passengers: list) -> dict:
    """
    Fetch air booking details from FlyHub API.

    Args:
        search_id (str): The FlyHub search ID.
        result_id (str): The FlyHub result ID.
        passengers (list): List of passenger details.

    Returns:
        dict: The response from the FlyHub API.

    Raises:
        HTTPException: If the request fails or an error occurs.
    """
    try:
        # Get a valid token (from cache or authenticate)
        token = get_flyhub_token()
        if not token:
            raise HTTPException(
                status_code=500,
                detail="FlyHub authentication failed. Token is None."
            )
        
        # Set up the API endpoint and headers
        url = f"{FLYHUB_BASE_URL}/AirBook"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        # Create the payload
        payload = {
            "SearchID": search_id,
            "ResultID": result_id,
            "Passengers": passengers
        }
        
        # Log the request
        logger.info(f"Sending AirBook request to FlyHub. URL: {url}")
        logger.info(f"Payload: {payload}")
        
        # Make the HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        
        # Raise for status if response indicates an error
        response.raise_for_status()
        
        # Log the response
        logger.info(f"FlyHub AirBook response: {response.json()}")
        return response.json()

    except httpx.HTTPStatusError as http_err:
        logger.error(f"FlyHub API returned an HTTP error: {http_err.response.text}")
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"FlyHub API Error: {http_err.response.text}"
        )

    except Exception as e:
        logger.exception(f"Unexpected error occurred while fetching FlyHub AirBook: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while fetching FlyHub AirBook: {str(e)}"
        )
    
    
async def fetch_flyhub_airprebook(search_id: str, result_id: str, passengers: list) -> dict:
    """
    Fetch air prebooking details from FlyHub API.

    Args:
        search_id (str): The FlyHub search ID.
        result_id (str): The FlyHub result ID.
        passengers (list): List of passenger details.

    Returns:
        dict: The response from the FlyHub API.

    Raises:
        HTTPException: If the request fails or an error occurs.
    """
    try:
        # Get a valid token (from cache or authenticate)
        token = get_flyhub_token()
        if not token:
            raise HTTPException(
                status_code=500,
                detail="FlyHub authentication failed. Token is None."
            )
        
        # Set up the API endpoint and headers
        url = f"{FLYHUB_BASE_URL}/AirPreBook"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        # Create the payload
        payload = {
            "SearchID": search_id,
            "ResultID": result_id,
            "Passengers": passengers
        }
        
        # Log the request
        logger.info(f"Sending AirPreBook request to FlyHub. URL: {url}")
        logger.info(f"Payload: {payload}")
        
        # Make the HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        
        # Raise for status if response indicates an error
        response.raise_for_status()
        
        # Log the response
        logger.info(f"FlyHub AirPreBook response: {response.json()}")
        return response.json()

    except httpx.HTTPStatusError as http_err:
        logger.error(f"FlyHub API returned an HTTP error: {http_err.response.text}")
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"FlyHub API Error: {http_err.response.text}"
        )

    except Exception as e:
        logger.exception(f"Unexpected error occurred while fetching FlyHub AirPreBook: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while fetching FlyHub AirPreBook: {str(e)}"
        )

async def fetch_flyhub_airprice(search_id: str, result_id: str):
    """
    Fetch air pricing details from FlyHub API.
    
    Args:
        search_id (str): The FlyHub search ID.
        result_id (str): The FlyHub result ID.
    
    Returns:
        dict: The response from the FlyHub API.
    
    Raises:
        HTTPException: If the request fails or an error occurs.
    """
    try:
        # Get a valid token (from cache or authenticate)
        token = get_flyhub_token()
        if not token:
            raise HTTPException(
                status_code=500,
                detail="FlyHub authentication failed. Token is None."
            )
        
        # Set up the API endpoint and headers
        url = f"{FLYHUB_BASE_URL}/AirPrice"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        # Create the payload
        payload = {
            "SearchID": search_id,
            "ResultID": result_id,
        }
        
        # Log the request
        logger.info(f"Sending AirPrice request to FlyHub. URL: {url}")
        logger.info(f"Payload: {payload}")
        
        # Make the HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        
        # Raise for status if response indicates an error
        response.raise_for_status()
        
        # Log the response
        logger.info(f"FlyHub AirPrice response: {response.json()}")
        return response.json()

    except httpx.HTTPStatusError as http_err:
        logger.error(f"FlyHub API returned an HTTP error: {http_err.response.text}")
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"FlyHub API Error: {http_err.response.text}"
        )

    except Exception as e:
        logger.exception(f"Unexpected error occurred while fetching FlyHub AirPrice: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while fetching FlyHub AirPrice: {str(e)}"
        )


async def fetch_flyhub_flights(payload: dict, page: int = 1, size: int = 50) -> dict:
    """
    Fetch flights from FlyHub API with a fallback to requests.
    Supports pagination using page and size parameters.
    """
    try:
        # Authenticate and get the token
        token = get_flyhub_token()
        if not token:
            raise HTTPException(
                status_code=500, detail="FlyHub authentication failed. Token is None."
            )

        # Validate FlyHub Base URL
        validate_url(FLYHUB_BASE_URL)

        # FlyHub API endpoint
        url = f"{FLYHUB_BASE_URL}/AirSearch"

        # Headers with the token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Add pagination to the payload
        payload["PageNumber"] = page
        payload["PageSize"] = size

        # Log the request payload
        logger.info(f"Sending request to FlyHub: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Payload: {payload}")

        # Attempt to fetch data using httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info("FlyHub response received successfully.")
            return response.json()
        else:
            logger.error(f"FlyHub API Error: {response.status_code}, {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"FlyHub API Error: {response.text}",
            )
    except Exception as httpx_exception:
        # Log the error and fall back to requests
        logger.error(f"HTTPX request failed: {httpx_exception}. Falling back to requests...")
        return fallback_to_requests(payload, page, size)


def fallback_to_requests(payload: dict, page: int = 1, size: int = 50) -> dict:
    """
    Fallback to requests if httpx fails.
    Supports pagination using page and size parameters.
    """
    validate_url(FLYHUB_BASE_URL)
    url = f"{FLYHUB_BASE_URL}/AirSearch"
    token = cached_token.get("token", None)

    if not token:
        raise HTTPException(
            status_code=500,
            detail="Cannot perform requests fallback: Missing authentication token.",
        )

    # Add pagination to the payload
    payload["PageNumber"] = page
    payload["PageSize"] = size

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        # Log the fallback request
        logger.info("Falling back to requests...")
        logger.info(f"Sending request to FlyHub via requests: {url}")

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            logger.info("FlyHub response received via requests fallback.")
            return response.json()
        else:
            logger.error(f"Requests API Error: {response.status_code}, {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Requests API Error: {response.text}",
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Requests fallback error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Requests fallback error: {str(e)}",
        )
