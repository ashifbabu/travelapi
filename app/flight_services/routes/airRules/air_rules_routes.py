from fastapi import APIRouter, Body, HTTPException, Depends
from typing import List
import logging

# Models and Service (adjust paths as per your project structure)
from app.flight_services.models.air_rules import AirRulesRequest, RouteFareRulesModel
from app.flight_services.services.air_rules_service import get_fare_rules_from_provider

router = APIRouter()
logger = logging.getLogger(__name__)

# Configure logging (if not already configured globally for your FastAPI app)
# This is often done in the main application setup
if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO) # Set your desired log level

@router.post(
    "/fare-rules",
    response_model=List[RouteFareRulesModel], # The endpoint will return a list of these
    summary="Fetch Fare Rules",
    description="Retrieves detailed fare rules for specified offers from a flight provider.",
    tags=["Flight Rules"] # Tag for API documentation
)
async def get_fare_rules_endpoint(
    request_payload: AirRulesRequest = Body(...)
):
    """
    Endpoint to fetch and process fare rules.

    - **traceId**: The unique trace identifier from a previous flight search or booking.
    - **offerIds**: A list of offer identifiers for which fare rules are being requested.
    """
    try:
        logger.info(f"Received fare rules request for traceId: {request_payload.traceId}")
        
        adapted_fare_rules = await get_fare_rules_from_provider(
            trace_id=request_payload.traceId,
            offer_id=request_payload.offerId
        )

        if not adapted_fare_rules:
            # This case might indicate that no rules were found,
            # or the provider call was successful but returned no data.
            # Depending on requirements, you might return 200 with empty list or 404.
            # For now, returning 200 with empty list is fine as per response_model.
            logger.info(f"No fare rules processed or found for traceId: {request_payload.traceId}, offerIds: {request_payload.offerIds}")
        
        return adapted_fare_rules # FastAPI will validate this against List[RouteFareRulesModel]

    except HTTPException as he:
        # Log the re-raised HTTPException details for monitoring
        logger.error(f"HTTPException in /fare-rules endpoint for traceId {request_payload.traceId}: Status {he.status_code}, Detail: {he.detail}")
        raise he # Re-raise to let FastAPI handle it
    except Exception as e:
        # Catch any other unexpected errors
        logger.exception(f"Unexpected critical error in /fare-rules endpoint for traceId {request_payload.traceId}: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal server error occurred while fetching fare rules.")