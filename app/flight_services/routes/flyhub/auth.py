from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

# FlyHub API credentials
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME", "thecityflyers@Gmail.com")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY", "g5TiX28v20Dg6BXkLpuTNUk7vEFCFo9igmOwXNvZulqKCoBHcO")
FLYHUB_PRODUCTION_URL = os.getenv("FLYHUB_PRODUCTION_URL", "https://api.flyhub.com/api/v1/")

@router.post("/authenticate")
async def authenticate():
    """
    Authenticate with FlyHub API to get the Bearer token.
    
    Returns:
        dict: Authentication token or error details.
    """
    url = f"{FLYHUB_PRODUCTION_URL}Authenticate"  # Authentication endpoint
    payload = {
        "username": FLYHUB_USERNAME,
        "apikey": FLYHUB_API_KEY
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()  # Token data
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error communicating with FlyHub API: {exc}")
