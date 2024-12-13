from fastapi import HTTPException
from app.flight_services.models.airretrieve.airretrieve_request import (
    UnifiedAirRetrieveRequest,
    UnifiedAirRetrieveResponse,
    FlyHubRetrieveRequest,
    BDFareRetrieveRequest,
)
from app.flight_services.clients.bdfare_client import fetch_bdfare_airretrieve
from app.flight_services.clients.flyhub_client import fetch_flyhub_airretrieve
import logging

# Initialize logger
logger = logging.getLogger("airretrieve_service")


async def fetch_airretrieve(payload: UnifiedAirRetrieveRequest) -> dict:
    """
    Fetch air retrieve details from the appropriate source.

    Args:
        payload (UnifiedAirRetrieveRequest): Unified request payload.

    Returns:
        dict: Raw response from the respective source.
    """
    source = payload.source.lower()

    if source == "bdfare":
        logger.info("Processing BDFare AirRetrieve request.")
        
        # Convert Unified Request to BDFare-specific Request
        bdfare_request = BDFareRetrieveRequest(orderReference=payload.bookingId)
        logger.debug(f"BDFare request: {bdfare_request.dict()}")
        
        # Fetch data from BDFare
        bdfare_response = await fetch_bdfare_airretrieve(bdfare_request.dict())
        logger.debug(f"BDFare response: {bdfare_response}")
        
        # Return raw response for now
        return bdfare_response

    elif source == "flyhub":
        logger.info("Processing FlyHub AirRetrieve request.")
        
        # Convert Unified Request to FlyHub-specific Request
        flyhub_request = FlyHubRetrieveRequest(BookingID=payload.bookingId)
        logger.debug(f"FlyHub request: {flyhub_request.dict()}")
        
        # Fetch data from FlyHub
        flyhub_response = await fetch_flyhub_airretrieve(flyhub_request.dict())
        logger.debug(f"FlyHub response: {flyhub_response}")
        
        # Return raw response for now
        return flyhub_response

    else:
        logger.error(f"Unsupported source: {source}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source: {source}",
        )
