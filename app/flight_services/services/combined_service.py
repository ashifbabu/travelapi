import asyncio
from fastapi import HTTPException
from app.flight_services.clients.bdfare_client import fetch_bdfare_flights
from app.flight_services.clients.flyhub_client import fetch_flyhub_flights
from app.flight_services.adapters.flyhub_adapter import convert_bdfare_to_flyhub
from app.flight_services.adapters.combined_search import format_flight_data_with_ids
# Removed: from app.cache import get_formatted_flights

async def combined_search(payload: dict, page: int = 1, size: int = 100) -> dict:
    """
    Perform a combined flight search using BDFare and FlyHub APIs based on the source.
    Pagination is applied at the external API call level (upstream).
    Caching functionality has been removed.

    Args:
        payload (dict): The flight search request payload.
        page (int): Page number for pagination.
        size (int): Number of results per page.

    Returns:
        dict: A unified structure containing the flight results.
    """
    try:
        # Assumes payload is Pydantic model, convert to dict
        request_payload = payload.dict()
        point_of_sale = request_payload.get("pointOfSale")
        source = request_payload.get("source")
        request_data = request_payload.get("request")

        if not source:
            raise ValueError("The 'source' key is missing in the payload.")
        if not point_of_sale:
            raise ValueError("The 'pointOfSale' key is missing in the payload.")
        if not request_data:
            raise ValueError("The 'request' key is missing in the payload.")

        enriched_request_data = {
            "pointOfSale": point_of_sale,
            "request": request_data,
        }

        raw_results = {}

        if source == "bdfare":
            raw_results["bdfare"] = await fetch_bdfare_flights(enriched_request_data, page=page, size=size)

        elif source == "flyhub":
            flyhub_payload = convert_bdfare_to_flyhub(request_data)
            raw_results["flyhub"] = await fetch_flyhub_flights(flyhub_payload, page=page, size=size)

        elif source == "all":
            flyhub_payload = convert_bdfare_to_flyhub(request_data)
            bdfare_task = fetch_bdfare_flights(enriched_request_data, page=page, size=size)
            flyhub_task = fetch_flyhub_flights(flyhub_payload, page=page, size=size)
            
            # Use return_exceptions=True to prevent one failing task from cancelling the other
            bdfare_response, flyhub_response = await asyncio.gather(
                bdfare_task, flyhub_task, return_exceptions=True
            )
            
            # Handle exceptions from gather if necessary, or assign results/None
            if isinstance(bdfare_response, Exception):
                 # Log the exception or handle specifically if needed
                 # logger.error("BDFare task failed", exc_info=bdfare_response)
                 bdfare_response = None # Or handle the error appropriately
            if isinstance(flyhub_response, Exception):
                 # Log the exception or handle specifically if needed
                 # logger.error("FlyHub task failed", exc_info=flyhub_response)
                 flyhub_response = None # Or handle the error appropriately

            raw_results["bdfare"] = bdfare_response
            raw_results["flyhub"] = flyhub_response

        else:
            raise ValueError(f"Invalid source specified: {source}")

        # Format the raw results directly, bypassing the cache function
        # Assumes format_flight_data_with_ids takes the raw_results dict
        # and returns the desired structured format.
        # Based on the original code, get_formatted_flights likely passed raw_results
        # to format_flight_data_with_ids.
        formatted_results = format_flight_data_with_ids(raw_results)

        # Return the formatted results in the expected structure
        return {"flights": formatted_results.get("Flights", [])}


    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Missing key in payload: {e}")
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Validation Error: {str(ve)}")
    except HTTPException as he:
        # Re-raise HTTPExceptions we intentionally raised
        raise he
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# for raw data

# import logging
# import asyncio
# from fastapi import HTTPException
# from app.flight_services.clients.bdfare_client import fetch_bdfare_flights
# from app.flight_services.clients.flyhub_client import fetch_flyhub_flights
# from app.flight_services.adapters.flyhub_adapter import convert_bdfare_to_flyhub

# # Initialize logger
# logger = logging.getLogger("combined_service")
# logger.setLevel(logging.INFO)

# async def combined_search(payload: dict, page: int = 1, size: int = 50) -> dict:
#     """
#     Perform a combined flight search using BDFare and FlyHub APIs based on the source.
#     This version returns the raw results without applying formatting or pagination.

#     Args:
#         payload (dict): Unified payload for flight search.
#         page (int): Page number for pagination (passed to service calls).
#         size (int): Number of results per page (passed to service calls).

#     Returns:
#         dict: Raw flight results from BDFare, FlyHub, or both.
#     """
#     try:
#         # Extract and log the request payload
#         request_payload = payload.dict()
#         logger.info(f"Processing request payload: {request_payload}")

#         # Extract pointOfSale, source, and request data
#         point_of_sale = request_payload.get("pointOfSale")
#         source = request_payload.get("source")
#         request_data = request_payload.get("request")

#         # Validate required keys
#         if not source:
#             raise ValueError("The 'source' key is missing in the payload.")
#         if not point_of_sale:
#             raise ValueError("The 'pointOfSale' key is missing in the payload.")
#         if not request_data:
#             raise ValueError("The 'request' key is missing in the payload.")

#         # Enrich request data
#         enriched_request_data = {
#             "pointOfSale": point_of_sale,
#             "request": request_data,
#         }
#         logger.info(f"Enriched request data for processing: {enriched_request_data}")

#         raw_results = {}

#         if source == "bdfare":
#             # Fetch raw results from BDFare
#             logger.info("Fetching results from BDFare...")
#             raw_results["bdfare"] = await fetch_bdfare_flights(enriched_request_data, page=page, size=size)

#         elif source == "flyhub":
#             # Transform payload for FlyHub
#             logger.info("Transforming payload for FlyHub...")
#             flyhub_payload = convert_bdfare_to_flyhub(request_data)
#             logger.info(f"Transformed FlyHub payload: {flyhub_payload}")

#             # Fetch raw results from FlyHub
#             logger.info("Fetching results from FlyHub...")
#             raw_results["flyhub"] = await fetch_flyhub_flights(flyhub_payload, page=page, size=size)

#         elif source == "all":
#             # Transform payload for FlyHub
#             logger.info("Transforming payload for FlyHub...")
#             flyhub_payload = convert_bdfare_to_flyhub(request_data)
#             logger.info(f"Transformed FlyHub payload: {flyhub_payload}")

#             # Fetch results from both BDFare and FlyHub concurrently
#             logger.info("Fetching results from both BDFare and FlyHub...")
#             bdfare_task = fetch_bdfare_flights(enriched_request_data, page=page, size=size)
#             flyhub_task = fetch_flyhub_flights(flyhub_payload, page=page, size=size)

#             # Await both tasks and handle errors individually
#             bdfare_response, flyhub_response = await asyncio.gather(
#                 bdfare_task, flyhub_task, return_exceptions=True
#             )

#             if isinstance(bdfare_response, Exception):
#                 logger.error(f"BDFare fetch error: {bdfare_response}")
#                 bdfare_response = None
#             else:
#                 logger.info(f"BDFare response: {bdfare_response}")

#             if isinstance(flyhub_response, Exception):
#                 logger.error(f"FlyHub fetch error: {flyhub_response}")
#                 flyhub_response = None
#             else:
#                 logger.info(f"FlyHub response: {flyhub_response}")

#             raw_results["bdfare"] = bdfare_response
#             raw_results["flyhub"] = flyhub_response

#         else:
#             raise ValueError(f"Invalid source specified: {source}")

#         logger.info(f"Raw results retrieved for source: {source}")
#         return raw_results

#     except KeyError as e:
#         logger.error(f"Missing key in payload: {e}")
#         raise HTTPException(status_code=422, detail=f"Missing key in payload: {e}")

#     except ValueError as ve:
#         logger.error(f"Validation error: {ve}")
#         raise HTTPException(status_code=422, detail=f"Validation Error: {str(ve)}")

#     except HTTPException as he:
#         logger.error(f"HTTP error: {he.detail}")
#         raise he

#     except Exception as e:
#         logger.exception("Unexpected error occurred during the flight search.")
#         raise HTTPException(
#             status_code=500, detail=f"An unexpected error occurred: {str(e)}"
#         )

