from fastapi import APIRouter, HTTPException, Depends
import httpx
import os

router = APIRouter()

# FlyHub API details
FLYHUB_PRODUCTION_URL = os.getenv("FLYHUB_PRODUCTION_URL", "https://api.flyhub.com/api/v1/")
AUTH_HEADER = {"Authorization": "Bearer <Replace_with_token>"}


@router.post("/search")
async def search_flights(payload: dict):
    """
    Search flights using the FlyHub API.
    
    Args:
        payload (dict): Flight search request payload.
        
    Returns:
        dict: The response from the FlyHub API.
    """
    url = f"{FLYHUB_PRODUCTION_URL}AirSearch"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=AUTH_HEADER)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error communicating with FlyHub API: {exc}")
