from fastapi import APIRouter, HTTPException, Depends
import httpx
import time
from .auth import cached_token  # Import the token cache

router = APIRouter()

# FlyHub API base URL
FLYHUB_PRODUCTION_URL = "https://api.flyhub.com/api/v1/"


@router.post("/search")
async def search_flights(payload: dict):
    """
    Search flights using the FlyHub API.

    Args:
        payload (dict): Flight search request payload.

    Returns:
        dict: The response from the FlyHub API.
    """
    global cached_token

    # Check if the token is still valid
    if cached_token["token"] is None or cached_token["expires_at"] < time.time():
        raise HTTPException(status_code=401, detail="Authentication token is missing or expired. Please re-authenticate.")

    url = f"{FLYHUB_PRODUCTION_URL}AirSearch"
    headers = {
        "Authorization": f"Bearer {cached_token['token']}",
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
        raise HTTPException(status_code=500, detail=f"Error communicating with FlyHub API: {exc}")
