from fastapi import APIRouter, HTTPException, Body
from app.flight_services.models.airretrieve.airretrieve_request import UnifiedAirRetrieveRequest
from app.flight_services.services.airretrieve_service import fetch_airretrieve
import logging

# Initialize the router and logger
router = APIRouter()
logger = logging.getLogger("airretrieve_routes")

@router.post("/retrieve", tags=["AirRetrieve"])
async def get_airretrieve(payload: UnifiedAirRetrieveRequest = Body(...)):
    """
    Endpoint to process AirRetrieve requests.
    """
    try:
        # Log the received request
        logger.info("Received AirRetrieve request.")
        logger.debug(f"Request payload: {payload.dict()}")

        # Process the request
        response = await fetch_airretrieve(payload)

        # Log the response
        logger.info("Returning AirRetrieve response.")
        return response

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Unexpected error during AirRetrieve processing.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
