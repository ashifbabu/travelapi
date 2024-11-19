from fastapi import APIRouter, HTTPException, Header
import httpx
import logging

# Initialize router
router = APIRouter()

# Directly embed BDFare API details
BDFARE_BASE_URL = "https://bdf.centralindia.cloudapp.azure.com/api/enterprise"
BDFARE_API_KEY = "Xm8yZms/ayM/Vm1UMTZZLUJ6Y2VlQDk1ZEZfJEtNLUdzUlF3WSUjQyo/JWd0aDZ5TmtzJnI0eXdBYyVRNz9DYQ=="

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import APIRouter

router = APIRouter()

@router.post("/airshopping")
async def air_shopping(payload: dict):
    return {"message": "AirShopping endpoint is working"}
