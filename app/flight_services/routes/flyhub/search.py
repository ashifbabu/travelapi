# from fastapi import APIRouter, HTTPException, Header
# import httpx
# import os
# import time

# router = APIRouter()

# # FlyHub API credentials and base URL
# FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME", "thecityflyers@Gmail.com")
# FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY", "g5TiX28v20Dg6BXkLpuTNUk7vEFCFo9igmOwXNvZulqKCoBHcO")
# FLYHUB_PRODUCTION_URL = os.getenv("FLYHUB_PRODUCTION_URL", "https://api.flyhub.com/api/v1/")

# # Token cache
# cached_token = {"token": None, "expires_at": 0}


# async def get_flyhub_token():
#     """
#     Authenticate with the FlyHub API to get a Bearer token.
#     Returns:
#         str: The Bearer token.
#     """
#     global cached_token

#     # Check if token is cached and still valid
#     current_time = time.time()
#     if cached_token["token"] and cached_token["expires_at"] > current_time:
#         return cached_token["token"]

#     # Authenticate with FlyHub API
#     auth_url = f"{FLYHUB_PRODUCTION_URL}Authenticate"
#     payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(auth_url, json=payload)

#         if response.status_code == 200:
#             token_data = response.json()
#             cached_token["token"] = token_data.get("TokenId")
#             cached_token["expires_at"] = current_time + 3600  # Default token validity: 1 hour
#             return cached_token["token"]
#         else:
#             raise HTTPException(status_code=response.status_code, detail="Authentication failed. Check your credentials.")
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=500, detail=f"Error communicating with FlyHub API: {exc}")


# @router.post("/search")
# async def search_flights(payload: dict):
#     """
#     Search flights using the FlyHub API.

#     Args:
#         payload (dict): The flight search request payload.

#     Returns:
#         dict: The response from the FlyHub API.
#     """
#     # Get token from cache or authenticate
#     token = await get_flyhub_token()

#     # Define FlyHub search URL
#     url = f"{FLYHUB_PRODUCTION_URL}AirSearch"
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }

#     try:
#         # Make the flight search request
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, json=payload, headers=headers)

#         if response.status_code == 200:
#             return response.json()
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)

#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=500, detail=f"Error communicating with FlyHub API: {exc}")

from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

# FlyHub API credentials and base URL
FLYHUB_PRODUCTION_URL = os.getenv("FLYHUB_PRODUCTION_URL", "https://api.flyhub.com/api/v1/")

# Directly provided FlyHub token (stored securely in the backend)
FLYHUB_TOKEN = os.getenv(
    "FLYHUB_TOKEN",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImN0eSI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6InRoZWNpdHlmbHllcnNAZ21haWwuY29tIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy91c2VyZGF0YSI6IjIwOTc4fDIxNTMxfDEwMy4xMjQuMjUxLjE0NywxMy4yMTUuMTgyLjcyIiwibmJmIjoxNzMxOTk3NzU5LCJleHAiOjE3MzI2MDI1NTksImlhdCI6MTczMTk5Nzc1OSwiaXNzIjoiaHR0cHM6Ly9hcGliZXRhLmZseWh1Yi5jb20iLCJhdWQiOiJhcGkuZmx5aHViLmNvbSJ9.lq5zvfBfyf5UdhVKaAqoMeEWbKZoLb6iTt9e690bXrg",
)

@router.post("/search")
async def search_flights(payload: dict):
    """
    Search flights using the FlyHub API.

    Args:
        payload (dict): The flight search request payload.

    Returns:
        dict: The response from the FlyHub API.
    """
    # Validate FlyHub API configuration
    if not FLYHUB_PRODUCTION_URL:
        raise HTTPException(status_code=500, detail="FlyHub production URL is not configured.")
    if not FLYHUB_TOKEN:
        raise HTTPException(status_code=500, detail="FlyHub token is not configured.")

    # Define FlyHub search URL and headers
    url = f"{FLYHUB_PRODUCTION_URL}AirSearch"
    headers = {
        "Authorization": f"Bearer {FLYHUB_TOKEN}",  # Token is added automatically here
        "Content-Type": "application/json",
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
