from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

# BDFare API details
BDFARE_URL = "https://bdf.centralindia.cloudapp.azure.com/api/enterprise/AirShopping"
BDFARE_API_KEY = "UEwqVXJHJjBXTE5pN0VwKi1WayF2R29UTmNaaTRLX1lVZFRzM09PNVNuMjAkQHkyVFUyI0FOR1JzRm1yQ0g3IQ=="

@router.post("/search")
async def search_flights(payload: dict):
    """
    Search flights using the BDFare API.
    
    Args:
        payload (dict): The flight search request payload.
        
    Returns:
        dict: The response from the BDFare API.
    """
    headers = {
        "X-API-KEY": BDFARE_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        # Send the request to BDFare
        async with httpx.AsyncClient() as client:
            response = await client.post(BDFARE_URL, json=payload, headers=headers)
        
        # Check the status code
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"An error occurred while connecting to BDFare: {exc}")
