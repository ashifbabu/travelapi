import asyncio
from fastapi import APIRouter, HTTPException, Body
from app.flight_services.clients.helpers import (
    convert_bdfare_to_flyhub,
    simplify_bdfare_response,
    simplify_flyhub_response,
)
from app.flight_services.clients.fetchers import fetch_bdfare_flights, fetch_flyhub_flights
from app.flight_services.models.combined.combined_search import RequestPayload

router = APIRouter()

@router.post("/search")
async def combined_search(payload: RequestPayload = Body(...)):
    """
    Perform a combined flight search using BDFare and FlyHub APIs.

    Args:
        payload (RequestPayload): The flight search request payload in BDFare format.

    Returns:
        dict: Simplified combined flight results from BDFare and FlyHub.
    """
    # Convert BDFare payload to FlyHub payload
    flyhub_payload = convert_bdfare_to_flyhub(payload.dict())

    try:
        # Fetch flight data concurrently from both APIs
        bdfare_task = fetch_bdfare_flights(payload.dict())
        flyhub_task = fetch_flyhub_flights(flyhub_payload)

        bdfare_response, flyhub_response = await asyncio.gather(bdfare_task, flyhub_task)

        # Simplify responses using helper functions
        simplified_bdfare = simplify_bdfare_response(bdfare_response)
        simplified_flyhub = simplify_flyhub_response(flyhub_response)

        # Combine results for output
        combined_results = {
            "bdfare": simplified_bdfare,
            "flyhub": simplified_flyhub,
        }

        return combined_results

    except Exception as e:
        # Handle exceptions and return HTTP errors
        raise HTTPException(status_code=500, detail=str(e))




# import asyncio
# from fastapi import APIRouter, HTTPException, Body
# from app.flight_services.clients.helpers import convert_bdfare_to_flyhub
# from app.flight_services.clients.fetchers import fetch_bdfare_flights, fetch_flyhub_flights
# from app.flight_services.models.combined.combined_search import RequestPayload

# router = APIRouter()

# @router.post("/search")
# async def combined_search(payload: RequestPayload = Body(...)):
#     """
#     Perform a combined flight search using BDFare and FlyHub APIs.

#     Args:
#         payload (RequestPayload): The flight search request payload in BDFare format.

#     Returns:
#         dict: Combined flight results from BDFare and FlyHub without simplification.
#     """
#     # Convert BDFare payload to FlyHub payload
#     flyhub_payload = convert_bdfare_to_flyhub(payload.dict())

#     try:
#         # Fetch flight data concurrently from both APIs
#         bdfare_task = fetch_bdfare_flights(payload.dict())
#         flyhub_task = fetch_flyhub_flights(flyhub_payload)

#         # Await responses from both APIs
#         bdfare_response, flyhub_response = await asyncio.gather(bdfare_task, flyhub_task)

#         # Combine results without simplifying
#         combined_results = {
#             "bdfare": bdfare_response,  # Return raw BDFare response
#             "flyhub": flyhub_response,  # Return raw FlyHub response
#         }

#         return combined_results

#     except Exception as e:
#         # Handle exceptions and return HTTP errors
#         raise HTTPException(status_code=500, detail=str(e))
