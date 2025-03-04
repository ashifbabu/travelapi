from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import os
import json
import subprocess
from dotenv import load_dotenv
import logging

# Load .env file
load_dotenv()

# Initialize router
router = APIRouter()

# Load BDFare API details from environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Pydantic models for request and response
class OrderReshopPriceRequest(BaseModel):
    orderReference: str = Field(..., example="BDF2401123")


class OrderReshopPriceResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


@router.post(
    "/orderreshopprice",
    response_model=OrderReshopPriceResponse,
    summary="Retrieve Order Reshop Price",
    description="Retrieve reshopped pricing details for an order using the BDFare API.",
)
async def order_reshop_price(payload: OrderReshopPriceRequest):
    """
    Retrieve reshopped pricing details for an order using BDFare API.

    Args:
        payload (OrderReshopPriceRequest): The request payload containing the order reference.

    Returns:
        OrderReshopPriceResponse: The response from the BDFare API.
    """
    if not BDFARE_BASE_URL:
        logger.error("BDFare Base URL is missing.")
        raise HTTPException(status_code=500, detail="BDFare Base URL is not configured.")
    if not BDFARE_API_KEY:
        logger.error("BDFare API Key is missing.")
        raise HTTPException(status_code=500, detail="BDFare API key is not configured.")

    url = f"{BDFARE_BASE_URL}/OrderReshopPrice"

    # Convert payload to JSON string for curl
    payload_json = json.dumps(payload.dict())

    # Construct the curl command
    curl_command = [
        "curl",
        "-X", "POST",
        url,
        "-H", f"X-API-KEY: {BDFARE_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", payload_json,
    ]

    logger.info(f"Executing curl command: {' '.join(curl_command)}")

    try:
        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)

        # Check for errors
        if result.returncode != 0:
            logger.error(f"Curl command failed: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )

        # Parse the response JSON
        response_data = json.loads(result.stdout)
        logger.debug(f"Curl Response: {response_data}")

        return OrderReshopPriceResponse(success=True, data=response_data)

    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from curl: {result.stdout}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to decode JSON response: {result.stdout}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error occurred using curl: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred using curl: {str(e)}"
        )
