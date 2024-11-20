import subprocess
import json
from fastapi import APIRouter, HTTPException
import httpx
import time

router = APIRouter()

# FlyHub API credentials
FLYHUB_USERNAME = "thecityflyers@gmail.com"
FLYHUB_API_KEY = "g5TiX28v20Dg6BXkLpuTNUk7vEFCFo9igmOwXNvZulqKCoBHcO"
FLYHUB_AUTH_URL = "https://api.flyhub.com/api/v1/Authenticate"
FLYHUB_AIRSEARCH_URL = "https://api.flyhub.com/api/v1/AirSearch"

# Token cache
cached_token = {"token": None, "expires_at": 0}


async def get_flyhub_token():
    """
    Authenticate with the FlyHub API to get a Bearer token.
    Returns:
        str: The Bearer token.
    """
    global cached_token

    # Check if token is cached and still valid
    current_time = time.time()
    if cached_token["token"] and cached_token["expires_at"] > current_time:
        return cached_token["token"]

    # Authenticate with FlyHub API
    payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(FLYHUB_AUTH_URL, json=payload)

        if response.status_code == 200:
            token_data = response.json()
            cached_token["token"] = token_data.get("TokenId")
            cached_token["expires_at"] = current_time + (7 * 24 * 3600)  # Token valid for 7 days
            return cached_token["token"]
        else:
            raise HTTPException(status_code=response.status_code, detail="Authentication failed. Check your credentials.")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error communicating with FlyHub API for authentication: {exc}")


@router.post("/search")
async def search_flights(payload: dict):
    """
    Search flights using the FlyHub API via curl.
    Args:
        payload (dict): The flight search request payload.
    Returns:
        dict: The response from the FlyHub API.
    """
    # Get the token
    token = await get_flyhub_token()

    # Convert payload to JSON string for curl
    payload_json = json.dumps(payload)

    # Construct the curl command
    curl_command = [
        "curl",
        "-X", "POST",
        FLYHUB_AIRSEARCH_URL,
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", payload_json
    ]

    try:
        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)

        # Check for errors
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )

        # Parse and return the JSON response
        response_json = json.loads(result.stdout)
        return response_json

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to decode JSON response: {result.stdout}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred: {str(e)}"
        )
