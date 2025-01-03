from app.flight_services.clients.bdfare_client import fetch_bdfare_flights
from app.flight_services.clients.flyhub_client import fetch_flyhub_flights
from app.flight_services.adapters.flyhub_adapter import convert_bdfare_to_flyhub
from app.flight_services.adapters.combined_search import format_flight_data_with_ids
from fastapi import HTTPException
import asyncio
import logging

logger = logging.getLogger("combined_service")

import asyncio
import logging
from fastapi import HTTPException
from app.flight_services.clients.bdfare_client import fetch_bdfare_flights
from app.flight_services.clients.flyhub_client import fetch_flyhub_flights
from app.flight_services.adapters.flyhub_adapter import convert_bdfare_to_flyhub
from app.flight_services.adapters.combined_search import format_flight_data_with_ids

logger = logging.getLogger("combined_service")

async def combined_search(payload):
    """
    Perform a combined flight search using BDFare and FlyHub APIs based on the source.

    Args:
        payload (dict): Unified payload for flight search.

    Returns:
        dict: Formatted flight results from BDFare, FlyHub, or both.
    """
    try:
        # Extract and log the request payload
        request_payload = payload.dict()
        logger.info(f"Processing request payload: {request_payload}")

        # Extract pointOfSale and source
        point_of_sale = request_payload.get("pointOfSale")
        source = request_payload.get("source")
        request_data = request_payload.get("request")

        # Validate required keys
        if not source:
            raise ValueError("The 'source' key is missing in the payload.")
        if not point_of_sale:
            raise ValueError("The 'pointOfSale' key is missing in the payload.")
        if not request_data:
            raise ValueError("The 'request' key is missing in the payload.")

        # Enrich request data
        enriched_request_data = {
            "pointOfSale": point_of_sale,
            "request": request_data,
        }
        logger.info(f"Enriched request data for processing: {enriched_request_data}")

        raw_results = {}

        if source == "bdfare":
            # Fetch raw results from BDFare
            logger.info("Fetching results from BDFare...")
            raw_results["bdfare"] = await fetch_bdfare_flights(enriched_request_data)

        elif source == "flyhub":
            # Transform payload for FlyHub
            logger.info("Transforming payload for FlyHub...")
            flyhub_payload = convert_bdfare_to_flyhub(request_data)
            logger.info(f"Transformed FlyHub payload: {flyhub_payload}")

            # Fetch raw results from FlyHub
            logger.info("Fetching results from FlyHub...")
            raw_results["flyhub"] = await fetch_flyhub_flights(flyhub_payload)

        elif source == "all":
            # Transform payload for FlyHub
            logger.info("Transforming payload for FlyHub...")
            flyhub_payload = convert_bdfare_to_flyhub(request_data)
            logger.info(f"Transformed FlyHub payload: {flyhub_payload}")

            # Fetch from both BDFare and FlyHub concurrently
            logger.info("Fetching results from both BDFare and FlyHub...")
            bdfare_task = fetch_bdfare_flights(enriched_request_data)
            flyhub_task = fetch_flyhub_flights(flyhub_payload)

            bdfare_response, flyhub_response = await asyncio.gather(bdfare_task, flyhub_task)

            logger.info(f"BDFare response: {bdfare_response}")
            logger.info(f"FlyHub response: {flyhub_response}")

            raw_results["bdfare"] = bdfare_response
            raw_results["flyhub"] = flyhub_response

        else:
            raise ValueError(f"Invalid source specified: {source}")

        logger.info(f"Raw results retrieved for source: {source}")

        # Format the raw results using the adapter
        formatted_results = format_flight_data_with_ids(raw_results)

        logger.info("Formatted flight search results successfully.")
        return formatted_results

    except KeyError as e:
        logger.error(f"Missing key in payload: {e}")
        raise HTTPException(status_code=422, detail=f"Missing key in payload: {e}")

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail=f"Validation Error: {str(ve)}")

    except HTTPException as he:
        logger.error(f"HTTP error: {he.detail}")
        raise he

    except Exception as e:
        logger.exception("Unexpected error occurred during the flight search.")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
