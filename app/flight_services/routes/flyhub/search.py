from fastapi import APIRouter, HTTPException, Header, Depends
import httpx
import time
from .auth import cached_token  # Import the cached token

router = APIRouter()

# FlyHub API base URL
FLYHUB_PRODUCTION_URL = "https://api.flyhub.com/api/v1/"


@router.post("/search")
async def search_flights(
    payload: dict,
    authorization: str = Header(None)  # Accept Authorization header
):
    """
    Search flights using the FlyHub API.

    Args:
        payload (dict): The flight search request payload.
        authorization (str): The Bearer token passed from the client.

    Returns:
        dict: The response from the FlyHub API.
    """
    global cached_token

    # Use the provided token or fallback to the cached token
    token = authorization.replace("Bearer ", "") if authorization else cached_token.get("token")

    # Check if the token is valid
    if not token:
        raise HTTPException(status_code=401, detail="Authentication token is missing. Please re-authenticate.")

    url = f"{FLYHUB_PRODUCTION_URL}AirSearch"
    headers = {
        "Authorization": f"Bearer {token}",
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
