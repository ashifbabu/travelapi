#app\flight_services\clients\bdfare_client.py
from typing import List
import httpx
import json
import requests
import asyncio
from typing import Dict, Any
from fastapi import HTTPException
import os
import logging
from dotenv import load_dotenv  # Import dotenv
from app.flight_services.adapters.airprebook_bdfare import adapt_to_bdfare_airprebook_request
from app.flight_services.adapters.bdfare_adapter import convert_to_bdfare_request
logger = logging.getLogger("bdfare_client")
# Load environment variables from .env file
load_dotenv()

# Load API credentials from environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")

# Validate environment variables
if not BDFARE_BASE_URL or not BDFARE_API_KEY:
    raise ValueError("Missing required BDFARE environment variables.")

# Example usage
print(f"BDFARE_BASE_URL: {BDFARE_BASE_URL}")
print(f"BDFARE_API_KEY: {BDFARE_API_KEY}")





logger = logging.getLogger("bdfare_client")

async def fetch_bdfare_ticket_cancel(payload: dict) -> dict:
    url = f"{BDFARE_BASE_URL}/OrderCancel"
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}

    logger.info(f"Sending Ticket Cancel request to BDFare: {url}")
    logger.debug(f"Payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
        logger.info(f"BDFare Ticket Cancel Response Status: {response.status_code}")
        logger.debug(f"BDFare Ticket Cancel Response Body: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception("Error during BDFare Ticket Cancel.")
        raise HTTPException(status_code=500, detail=f"Error in BDFare Ticket Cancel: {str(e)}")

async def fetch_bdfare_ticket_issue(payload: dict) -> dict:
    """
    Fetch ticket issue details from BDFare API.
    """
    url = f"{BDFARE_BASE_URL}/OrderChange"
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}

    logger.info(f"Sending Ticket Issue request to BDFare: {url}")
    logger.debug(f"Payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
        logger.info(f"BDFare Ticket Issue Response Status: {response.status_code}")
        logger.debug(f"BDFare Ticket Issue Response Body: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception("Error during BDFare Ticket Issue.")
        raise HTTPException(status_code=500, detail=f"Error in BDFare Ticket Issue: {str(e)}")

async def fetch_bdfare_airretrieve(payload: dict) -> dict:
    """
    Fetch booking details from BDFare API.

    Args:
        payload (dict): Request payload with `orderReference`.

    Returns:
        dict: Response from the BDFare API.

    Raises:
        HTTPException: If an error occurs during the request.
    """
    url = f"{BDFARE_BASE_URL}/OrderRetrieve"
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}

    logger.info(f"Sending AirRetrieve request to BDFare: {url}")
    logger.debug(f"Payload: {payload}")

    try:
        # Make the POST request to BDFare API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)

        logger.info(f"BDFare AirRetrieve Response Status: {response.status_code}")
        logger.debug(f"BDFare AirRetrieve Response Body: {response.text}")

        # Raise for HTTP errors
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as exc:
        logger.error(f"BDFare API Error: {exc.response.text}")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"BDFare API returned error: {exc.response.text}",
        )
    except Exception as e:
        logger.exception("Unexpected error during BDFare AirRetrieve request.")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error fetching BDFare AirRetrieve: {str(e)}",
        )
async def fetch_bdfare_airbook(trace_id: str, offer_ids: List[str], request: dict) -> dict:
    """
    Fetch air booking from BDFare API.

    Args:
        trace_id (str): Unique trace ID for the booking.
        offer_ids (List[str]): List of offer IDs related to the booking.
        request (dict): The request payload with passenger and contact details.

    Returns:
        dict: The response from the BDFare API.

    Raises:
        HTTPException: If an error occurs during the request.
    """
    url = f"{BDFARE_BASE_URL}/OrderCreate"
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}

    # Construct the payload
    payload = {
        "traceId": trace_id,
        "offerId": offer_ids,
        "request": request,
    }

    logger.info(f"Sending BDFare AirBook request to {url}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Payload: {payload}")

    try:
        # Send the POST request to the BDFare API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)

        # Log the response status and body
        logger.info(f"BDFare AirBook Response Status: {response.status_code}")
        logger.debug(f"Response Headers: {response.headers}")
        logger.debug(f"Response Body: {response.text}")

        # Raise an exception if the response status is an HTTP error
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as exc:
        # Handle HTTP errors and log detailed information
        error_message = exc.response.text or "No error details provided"
        logger.error(f"BDFare API Error: {error_message}")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"BDFare API returned error: {error_message}"
        )

    except Exception as e:
        # Handle unexpected exceptions
        logger.exception("Unexpected error during BDFare AirBook request.")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error fetching BDFare AirBook: {str(e)}"
        )

async def fetch_bdfare_airprebook(trace_id: str, offer_ids: List[str], request: dict) -> dict:
    """
    Fetch air prebooking from BDFare API.
    """
    url = f"{BDFARE_BASE_URL}/OrderSell"
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}

    payload = {
        "traceId": trace_id,
        "offerId": offer_ids,
        "request": request
    }

    logger.info(f"Sending BDFare AirPrebook request to {url}")
    logger.info(f"Request Payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
        
        logger.info(f"BDFare Response Status: {response.status_code}")
        logger.debug(f"BDFare Response Body: {response.text}")

        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(f"BDFare API Error: {exc.response.text}")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"BDFare API returned error: {exc.response.text}"
        )
    except Exception as e:
        logger.exception("Unexpected error during BDFare AirPrebook request.")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error fetching BDFare AirPrebook: {str(e)}"
        )

async def fetch_bdfare_airprice(trace_id: str, offer_ids: list) -> dict:
    """
    Fetch air pricing from BDFare API.
    """
    url = f"{BDFARE_BASE_URL}/OfferPrice"
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}
    payload = {"traceId": trace_id, "offerId": offer_ids}

    logger.info(f"Sending request to BDFare API. URL: {url}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:  # Increased timeout to 60 seconds
            response = await client.post(url, json=payload, headers=headers)

        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Body: {response.text}")

        response.raise_for_status()  # Raise exception for 4xx/5xx errors
        return response.json()

    except httpx.ReadTimeout as exc:
        logger.error(f"BDFare API request timed out: {exc}")
        raise HTTPException(status_code=500, detail="The BDFare API request timed out.")

    except httpx.RequestError as exc:
        logger.error(f"Request error while contacting BDFare API: {exc}")
        raise HTTPException(status_code=500, detail=f"An error occurred while contacting BDFare API: {exc}")

    except httpx.HTTPStatusError as exc:
        logger.error(f"BDFare API error. Status Code: {exc.response.status_code}, Detail: {exc.response.text}")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"BDFare API Error: {exc.response.text}"
        )
    
async def fetch_bdfare_flights(payload: dict, page: int = 1, size: int = 50) -> dict:
    """
    Fetch flights from BDFare API with pagination support and a fallback to a synchronous call wrapped in an executor.
    """
    # Transform the payload and add pagination
    transformed_payload = convert_to_bdfare_request(payload)
    transformed_payload["PageNumber"] = page
    transformed_payload["PageSize"] = size

    url = f"{BDFARE_BASE_URL}/AirShopping"
    headers = {
        "X-API-KEY": BDFARE_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=transformed_payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"BDFare API Error: {response.text}"
            )
    except Exception:
        # If httpx fails, fallback to the synchronous request using run_in_executor
        return await fallback_to_requests_async(url, transformed_payload, page, size)


async def fallback_to_requests_async(url: str, payload: dict, page: int = 1, size: int = 50) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: fallback_to_requests(url, payload, page, size))


def fallback_to_requests(url: str, payload: dict, page: int = 1, size: int = 50) -> dict:
    """
    Fallback using the requests library if httpx fails.
    """
    payload["PageNumber"] = page
    payload["PageSize"] = size

    headers = {
        "X-API-KEY": BDFARE_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad status codes
        return response.json()
    except requests.exceptions.HTTPError:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"HTTP request failed: {response.text}"
        )
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(
            status_code=500,
            detail=f"Network or request error during API call: {str(req_err)}"
        )
    except json.JSONDecodeError as json_err:
        raise HTTPException(
            status_code=500,
            detail=f"JSON decoding failed: {str(json_err)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

# Dummy convert_to_bdfare_request for completeness (replace with your actual implementation)
def convert_to_bdfare_request(payload: dict) -> dict:
    return payload