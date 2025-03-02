from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from app.flight_services.models.combined.combined_search import FlightSearchRequest
from app.flight_services.services.combined_service import combined_search
import logging

# Initialize the router and logger
router = APIRouter()
logger = logging.getLogger("combined_search")
logger.setLevel(logging.INFO)

# Configure logging (if not already configured globally)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


@router.post("/search")
async def search_flights(
    payload: FlightSearchRequest = Body(...),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    size: int = Query(100, ge=1, le=100, description="Number of results per page (max 100)"),
):
    try:
        # Call the combined search service
        results = await combined_search(payload, page=page, size=size)

        # Previously, you sliced the results here...
        # total_results = len(results["flights"])
        # start = (page - 1) * size
        # end = start + size
        # paginated_flights = results["flights"][start:end]

        # Return paginated response with metadata
        response = {
            "page": page,
            "size": size,
            "flights": results["flights"],
        }
        return response

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Validation Error: {str(ve)}")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )




# for raw data

# from fastapi import APIRouter, Body, HTTPException, Query
# from fastapi.middleware.gzip import GZipMiddleware
# from app.flight_services.models.combined.combined_search import FlightSearchRequest
# from app.flight_services.services.combined_service import combined_search
# import logging

# # Initialize the router and logger
# router = APIRouter()
# logger = logging.getLogger("combined_search")
# logger.setLevel(logging.INFO)

# # Configure logging (if not already configured globally)
# console_handler = logging.StreamHandler()
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)

# @router.post("/search")
# async def search_flights(
#     payload: FlightSearchRequest = Body(...),
#     page: int = Query(1, ge=1, description="Page number for pagination"),
#     size: int = Query(100, ge=1, le=100, description="Number of results per page (max 100)"),
# ):
#     """
#     Perform a combined flight search based on the specified source.
    
#     For testing purposes, this endpoint returns the raw result from the combined_search service
#     without applying formatting or pagination.
    
#     Args:
#         payload (FlightSearchRequest): The flight search request payload.
#         page (int): The page number (passed to the service).
#         size (int): The number of results per page (passed to the service).
    
#     Returns:
#         dict: The raw flight results as provided by the combined_search service.
#     """
#     try:
#         logger.info("Received search request: %s", payload.dict())

#         # Call the combined search service
#         results = await combined_search(payload, page=page, size=size)
        
#         # Since the raw results are not wrapped inside a "flights" key anymore,
#         # we just return them directly.
#         logger.info("Returning raw search results for testing.")
#         return results

#     except ValueError as ve:
#         logger.error("Validation error: %s", str(ve))
#         raise HTTPException(status_code=422, detail=f"Validation Error: {str(ve)}")

#     except HTTPException as he:
#         logger.error("HTTP error: %s", he.detail)
#         raise he

#     except Exception as e:
#         logger.exception("Unexpected error occurred during the flight search.")
#         raise HTTPException(
#             status_code=500, detail=f"An unexpected error occurred: {str(e)}"
#         )
