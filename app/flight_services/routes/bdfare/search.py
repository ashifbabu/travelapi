from fastapi import APIRouter, HTTPException, Header, Depends
import httpx
import os
from dotenv import load_dotenv
import logging

# Load .env file
load_dotenv()

# Initialize router
router = APIRouter()

# Load BDFare API details from environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/airshopping")
async def search_flights(payload: dict):
    """
    Search and retrieve flight results using BDFare API.

    Args:
        payload (dict): The flight search request payload.

    Returns:
        dict: The response from the BDFare API.
    """
    if not BDFARE_BASE_URL:
        logger.error("BDFare Base URL is missing.")
        raise HTTPException(status_code=500, detail="BDFare Base URL is not configured.")
    if not BDFARE_API_KEY:
        logger.error("BDFare API Key is missing.")
        raise HTTPException(status_code=500, detail="BDFare API key is not configured.")

    url = f"{BDFARE_BASE_URL}/AirShopping"
    headers = {
        "X-API-KEY": BDFARE_API_KEY,
        "Content-Type": "application/json",
    }

    logger.info(f"Making request to BDFare API: {url}")
    logger.debug(f"Payload: {payload}")

    try:
        # Make the flight search request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        logger.info(f"BDFare API responded with status code: {response.status_code}")

        if response.status_code == 200:
            logger.debug(f"Response: {response.json()}")
            return response.json()
        else:
            logger.error(f"Error response from BDFare API: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"BDFare API error: {response.text}",
            )

    except httpx.RequestError as exc:
        logger.exception(f"Error communicating with BDFare API: {exc}")
        raise HTTPException(
            status_code=500, detail=f"Error communicating with BDFare API: {str(exc)}"
        )
