from fastapi import APIRouter, HTTPException, Body
from pydantic import ValidationError
from app.flight_services.models.airbook.airbook_request import UnifiedAirBookRequest
from app.flight_services.services.airbook_service import fetch_airbook, fetch_bdfare_airbook
import logging

# Initialize the router and logger
router = APIRouter()
logger = logging.getLogger("airbook_routes")

@router.post("/book", tags=["AirBook"])
async def get_airbook(payload: UnifiedAirBookRequest = Body(...)):
    print("Received AirBook request.")
    print("Request Payload:", payload.dict())
    """
    Endpoint to process air booking requests for supported sources.
    """
    try:
        logger.info("Received AirBook request.")
        logger.debug(f"Request payload: {payload.dict()}")
        
        response = await fetch_airbook(payload)
        logger.info("Returning AirBook response.")
        return response
    except ValidationError as ve:
        logger.error("Validation Error in request payload.", exc_info=ve)
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Unexpected error during AirBook processing.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
