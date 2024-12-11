from fastapi import APIRouter, HTTPException, Body
from pydantic import ValidationError
from app.flight_services.models.airprebook.airprebook_request import UnifiedAirPrebookRequest
from app.flight_services.services.airprebook_service import fetch_airprebook
import logging

# Initialize the router and logger
router = APIRouter()
logger = logging.getLogger("airprebook_routes")

@router.post("/prebook", tags=["AirPrebook"])
async def get_airprebook(payload: UnifiedAirPrebookRequest = Body(...)):
    """
    Endpoint to process air prebook requests for supported sources.
    """
    try:
        logger.info("Received AirPrebook request.")
        logger.debug(f"Request payload: {payload.dict()}")
        response = await fetch_airprebook(payload)
        logger.info("Returning AirPrebook response.")
        return response
    except ValidationError as ve:
        logger.error("Validation Error in request payload.", exc_info=ve)
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Unexpected error during AirPrebook processing.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")