from fastapi import APIRouter, HTTPException
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Load configuration from environment variables
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")
FLYHUB_PRODUCTION_URL = os.getenv("FLYHUB_PRODUCTION_URL")

router = APIRouter(prefix="/flyhub")

class FlyhubAuthClient:
    def __init__(self):
        self.auth_token = None

    def authenticate(self):
        """
        Authenticate with Flyhub API and retrieve a token.
        """
        payload = {
            "username": FLYHUB_USERNAME,
            "apikey": FLYHUB_API_KEY
        }
        response = requests.post(f"{FLYHUB_PRODUCTION_URL}Authenticate", json=payload)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        data = response.json()
        if "TokenId" not in data:
            raise HTTPException(status_code=500, detail="Token not found in response.")
        self.auth_token = data.get("TokenId")
        return self.auth_token

flyhub_auth_client = FlyhubAuthClient()

@router.post("/authenticate", tags=["Flights"])
def authenticate():
    """
    Endpoint to authenticate with Flyhub API and return the token.
    """
    try:
        token = flyhub_auth_client.authenticate()
        return {"token": token}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
