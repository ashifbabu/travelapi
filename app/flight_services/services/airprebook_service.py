from app.flight_services.clients.bdfare_client import fetch_bdfare_airprebook
from app.flight_services.clients.flyhub_client import fetch_flyhub_airprebook
from app.flight_services.adapters.airprebook_flyhub import convert_bdfare_to_flyhub_airprebook_request
from app.flight_services.adapters.airprebook_bdfare import adapt_to_bdfare_airprebook_request

import logging
from fastapi import HTTPException

from app.flight_services.models.airprebook.airprebook_request import UnifiedAirPrebookRequest

logger = logging.getLogger("airprebook_service")

async def fetch_airprebook(payload: UnifiedAirPrebookRequest) -> dict:
    """
    Determine source and fetch air prebooking accordingly.
    Currently supports 'bdfare' and 'flyhub' as sources.

    Args:
        payload (UnifiedAirPrebookRequest): The unified payload for air prebooking.

    Returns:
        dict: The response from the respective API.

    Raises:
        HTTPException: If the source is unsupported or an error occurs.
    """
    source = payload.source.lower()

    if source == "bdfare":
        logger.info("Processing BDFare AirPrebook request.")
        bdfare_request = adapt_to_bdfare_airprebook_request(payload.dict())
        logger.debug(f"Transformed request for BDFare: {bdfare_request}")
        return await fetch_bdfare_airprebook(
            trace_id=bdfare_request["traceId"],
            offer_ids=bdfare_request["offerId"],
            request=bdfare_request["request"]
        )
    elif source == "flyhub":
        logger.info("Processing FlyHub AirPrebook request.")
        flyhub_request = convert_bdfare_to_flyhub_airprebook_request(payload.dict())
        logger.debug(f"Transformed request for FlyHub: {flyhub_request}")
        return await fetch_flyhub_airprebook(
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
