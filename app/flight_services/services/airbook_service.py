import logging
from fastapi import HTTPException
from app.flight_services.clients.bdfare_client import fetch_bdfare_airbook
from app.flight_services.clients.flyhub_client import fetch_flyhub_airbook
from app.flight_services.adapters.airbook_bdfare import adapt_to_bdfare_airbook_request
from app.flight_services.adapters.airbook_flyhub import convert_flyhub_to_bdfare_airbook_request
from app.flight_services.models.airbook.airbook_request import UnifiedAirBookRequest

logger = logging.getLogger("airbook_service")

async def fetch_airbook(payload: UnifiedAirBookRequest) -> dict:
    """
    Determine source and fetch air booking accordingly.
    Currently supports 'bdfare' and 'flyhub' as sources.

    Args:
        payload (UnifiedAirBookRequest): The unified payload for air booking.

    Returns:
        dict: The response from the respective API.

    Raises:
        HTTPException: If the source is unsupported or an error occurs.
    """
    source = payload.source.lower()

    if source == "bdfare":
        logger.info("Processing BDFare AirBook request.")
        bdfare_request = adapt_to_bdfare_airbook_request(payload.dict())
        logger.debug(f"Transformed request for BDFare: {bdfare_request}")
        return await fetch_bdfare_airbook(
            trace_id=bdfare_request["traceId"],
            offer_ids=bdfare_request["offerId"],
            request=bdfare_request["request"]
        )
    elif source == "flyhub":
        logger.info("Processing FlyHub AirBook request.")
        flyhub_request = convert_flyhub_to_bdfare_airbook_request(payload.dict())
        logger.debug(f"Transformed request for FlyHub: {flyhub_request}")
        return await fetch_flyhub_airbook(
            search_id=flyhub_request["SearchID"],
            result_id=flyhub_request["ResultID"],
            passengers=flyhub_request["Passengers"]
        )
    else:
        logger.error(f"Unsupported source: {source}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source: {source}"
        )
