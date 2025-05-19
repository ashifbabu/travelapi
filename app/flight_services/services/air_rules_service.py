import logging
from typing import List, Dict, Any
from fastapi import HTTPException

# BDFare Client and Adapter (adjust paths as per your project structure)
from app.flight_services.clients.bdfare_client import fetch_bdfare_farerules
from app.flight_services.adapters.airrules_bdfare import adapt_bdfare_fare_rules, AdaptedRouteFareRules

# Model for type hinting the adapted response if needed, though TypedDict is also fine
from app.flight_services.models.air_rules import RouteFareRulesModel


logger = logging.getLogger(__name__)

async def get_fare_rules_from_provider(
    trace_id: str,
    offer_id: str  # Changed from offer_ids: List[str]
) -> List[AdaptedRouteFareRules]:
    """
    Fetches and adapts fare rules from BDFare for a single offer.
    """
    try:
        logger.info(f"Fetching fare rules from BDFare for traceId: {trace_id}, offerId: {offer_id}")
        raw_bdfare_rules_response: Dict[str, Any] = await fetch_bdfare_farerules(
            trace_id=trace_id,
            offer_id=offer_id # Pass the single offer_id
        )
        # ... (rest of the function remains the same) ...
        if not raw_bdfare_rules_response:
            logger.warning(f"Received empty response from BDFare client for fare rules. TraceId: {trace_id}, OfferId: {offer_id}")
            return []

        logger.info(f"Adapting BDFare fare rules response for traceId: {trace_id}, OfferId: {offer_id}")
        adapted_rules: List[AdaptedRouteFareRules] = adapt_bdfare_fare_rules(raw_bdfare_rules_response)

        if not adapted_rules and raw_bdfare_rules_response.get("success", False):
             logger.info(f"Fare rules adaptation resulted in an empty list for traceId: {trace_id}, OfferId: {offer_id}, though provider call was successful.")
        elif not adapted_rules:
             logger.warning(f"Fare rules adaptation resulted in an empty list for traceId: {trace_id}, OfferId: {offer_id}.")
        return adapted_rules

    except HTTPException as he:
        logger.error(f"HTTPException while getting fare rules for traceId {trace_id}, OfferId {offer_id}: {he.detail}")
        raise he
    except Exception as e:
        logger.exception(f"Unexpected error fetching or adapting fare rules for traceId {trace_id}, OfferId {offer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing fare rules: {str(e)}")