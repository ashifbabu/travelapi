from fastapi import APIRouter, HTTPException
import requests
import os
from dotenv import load_dotenv

load_dotenv()

FLYHUB_AUTH_URL = os.getenv("FLYHUB_PRODUCTION_URL") + "auth"
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")

router = APIRouter()

class FlyhubAuthClient:
    def __init__(self):
        self.auth_token = None

    def authenticate(self):
        payload = {
            "username": FLYHUB_USERNAME,
            "apikey": FLYHUB_API_KEY
        }
        response = requests.post(FLYHUB_AUTH_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        self.auth_token = data.get("token")
        return self.auth_token

flyhub_auth_client = FlyhubAuthClient()

@router.get("/authenticate")
def authenticate():
    """Endpoint to authenticate with Flyhub API and return the token."""
    try:
        token = flyhub_auth_client.authenticate()
        if not token:
            raise HTTPException(status_code=400, detail="Authentication failed. No token received.")
        return {"token": token}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")