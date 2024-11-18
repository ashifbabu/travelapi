from fastapi import APIRouter, HTTPException, Header
import httpx
import os

router = APIRouter()

# Load BDFare API details from environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")


@router.post("/airshopping")
async def search_flights(payload: dict):
    """
    Search and retrieve flight results using BDFare API.

    Args:
        payload (dict): The flight search request payload.

    Returns:
        dict: The response from the BDFare API.
    """
    # Use the API key from the .env file
    api_key = BDFARE_API_KEY

    if not api_key:
        raise HTTPException(status_code=400, detail="API key is missing.")

    url = f"{BDFARE_BASE_URL}/AirShopping"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    try:
        # Make the flight search request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error communicating with BDFare API: {exc}")
