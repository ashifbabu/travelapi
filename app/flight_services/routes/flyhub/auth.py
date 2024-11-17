from fastapi import APIRouter, HTTPException
import httpx
import os
import time

router = APIRouter()

# FlyHub API credentials
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME", "thecityflyers@Gmail.com")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY", "g5TiX28v20Dg6BXkLpuTNUk7vEFCFo9igmOwXNvZulqKCoBHcO")
FLYHUB_PRODUCTION_URL = os.getenv("FLYHUB_PRODUCTION_URL", "https://api.flyhub.com/api/v1/")

# Token cache
cached_token = {"token": None, "expires_at": 0}


@router.post("/authenticate")
async def authenticate():
    """
    Authenticate with FlyHub API to get a Bearer token.

    Returns:
        dict: Contains the Bearer token and expiration time.
    """
    global cached_token
    url = f"{FLYHUB_PRODUCTION_URL}Authenticate"
    payload = {
        "username": FLYHUB_USERNAME,
        "apikey": FLYHUB_API_KEY
    }

    try:
        # Make the authentication request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            token_data = response.json()
            # Cache the token and expiration time
            cached_token["token"] = token_data["token"]
            cached_token["expires_at"] = time.time() + token_data.get("expires_in", 3600)  # Default to 1 hour if not provided
            return token_data
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error communicating with FlyHub API: {exc}")
