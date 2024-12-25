import httpx
import logging

BASE_URL = "https://api.portapi.com"

logger = logging.getLogger("portapi_client")

async def fetch_airport_name(iata_code):
    """
    Fetch airport name by IATA code using PortAPI.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Use the endpoint without adding any authorization headers
            url = f"{BASE_URL}/airport/iata/{iata_code}"
            response = await client.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            # Extract and return the airport name
            return data.get("properties", {}).get("name", "Unknown Airport")
    except httpx.HTTPStatusError as e:
        logger.error(f"PortAPI HTTP Error: {e.response.status_code} - {e.response.text}")
        return "Unknown Airport"
    except Exception as e:
        logger.error(f"PortAPI Request Error: {e}")
        return "Unknown Airport"
