# app/flight_services/adapters/airrules_bdfare.py

import logging
from typing import Dict, List, Any, Optional, TypedDict

logger = logging.getLogger(__name__)

# --- Define TypedDicts for the adapted (output) structure ---
class AdaptedRuleDetail(TypedDict):
    """Represents a single rule category and its textual information."""
    category_name: str  # e.g., "Rule Application", "Penalties"
    rules_text: str     # The detailed text for this category

class AdaptedPaxFareRules(TypedDict):
    """Represents fare rules for a specific passenger type and fare basis code on a route."""
    pax_type: str           # e.g., "Adult"
    fare_basis_code: str    # e.g., "EDOMO"
    rule_details: List[AdaptedRuleDetail] # List of rule categories and their text

class AdaptedRouteFareRules(TypedDict):
    """Represents fare rules for a specific route, containing rules for various passenger types."""
    route: str  # e.g., "DAC→JSR"
    pax_specific_rules: List[AdaptedPaxFareRules] # List of rules per passenger type

# --- Adapter Function ---
def adapt_bdfare_fare_rules(bdfare_rules_response: Dict[str, Any]) -> List[AdaptedRouteFareRules]:
    """
    Adapts the BDFare /FareRules API response to a structured internal format.

    The BDFare response structure is expected to be:
    {
        "response": {
            "fareRuleRouteInfos": [
                {
                    "route": "...",
                    "fareRulePaxInfos": [
                        {
                            "paxType": "...",
                            "fareBasisCode": "...",
                            "fareRuleInfos": [
                                {"category": "...", "info": "..."},
                                ...
                            ]
                        },
                        ...
                    ]
                },
                ...
            ],
            "traceId": "..."
            # ... other response fields
        },
        # ... other top-level fields like message, statusCode, success
    }

    Args:
        bdfare_rules_response: The raw JSON response dictionary from the BDFare /FareRules API.

    Returns:
        A list of AdaptedRouteFareRules objects. Returns an empty list if
        the input is invalid, contains errors, or has no processable rule information.
    """
    adapted_route_rules_list: List[AdaptedRouteFareRules] = []

    if not bdfare_rules_response or not isinstance(bdfare_rules_response, dict):
        logger.warning("BDFare fare rules response is empty or not a valid dictionary.")
        return adapted_route_rules_list

    # Check for top-level success and errors first
    if not bdfare_rules_response.get("success", False):
        logger.error(
            f"BDFare API call was not successful. Status: {bdfare_rules_response.get('statusCode')}, "
            f"Message: {bdfare_rules_response.get('message')}, Error: {bdfare_rules_response.get('error')}"
        )
        return adapted_route_rules_list

    response_data = bdfare_rules_response.get("response")
    if not response_data or not isinstance(response_data, dict):
        logger.warning("Missing or invalid 'response' object in BDFare fare rules data.")
        return adapted_route_rules_list
    
    # Optional: You might want to capture and return the traceId from response_data.get("traceId")
    # if it's useful for the calling context. For now, the adapter focuses on rules.

    fare_rule_route_infos = response_data.get("fareRuleRouteInfos")
    if not isinstance(fare_rule_route_infos, list):
        logger.warning("No 'fareRuleRouteInfos' list found in response data, or it's not a list.")
        if response_data.get("error"): # Check for errors within the 'response' object
             logger.error(f"BDFare 'response' object contained an error: {response_data.get('error')}")
        return adapted_route_rules_list
    
    if not fare_rule_route_infos:
        logger.info("BDFare 'fareRuleRouteInfos' list is present but empty.")
        return adapted_route_rules_list

    for route_info_data in fare_rule_route_infos:
        if not isinstance(route_info_data, dict):
            logger.warning(f"Skipping an item in 'fareRuleRouteInfos' as it's not a dictionary: {route_info_data}")
            continue

        route_str = route_info_data.get("route")
        if not route_str or not isinstance(route_str, str):
            logger.warning(f"Skipping route info due to missing or invalid 'route': {route_info_data}")
            continue

        current_route_pax_rules: List[AdaptedPaxFareRules] = []
        fare_rule_pax_infos = route_info_data.get("fareRulePaxInfos")

        if not isinstance(fare_rule_pax_infos, list):
            logger.warning(f"No 'fareRulePaxInfos' found or not a list for route '{route_str}'.")
        else:
            for pax_info_data in fare_rule_pax_infos:
                if not isinstance(pax_info_data, dict):
                    logger.warning(f"Skipping an item in 'fareRulePaxInfos' for route '{route_str}' as it's not a dictionary: {pax_info_data}")
                    continue

                pax_type = pax_info_data.get("paxType", "UNKNOWN")
                if not isinstance(pax_type, str): pax_type = str(pax_type)
                
                fare_basis_code = pax_info_data.get("fareBasisCode", "UNKNOWN")
                if not isinstance(fare_basis_code, str): fare_basis_code = str(fare_basis_code)
                
                current_pax_rule_details: List[AdaptedRuleDetail] = []
                fare_rule_infos = pax_info_data.get("fareRuleInfos")

                if not isinstance(fare_rule_infos, list):
                    logger.warning(f"No 'fareRuleInfos' found or not a list for route '{route_str}', paxType '{pax_type}'.")
                else:
                    for rule_info_data in fare_rule_infos:
                        if not isinstance(rule_info_data, dict):
                            logger.warning(
                                f"Skipping an item in 'fareRuleInfos' for route '{route_str}', paxType '{pax_type}' "
                                f"as it's not a dictionary: {rule_info_data}"
                            )
                            continue
                        
                        category = rule_info_data.get("category", "GENERAL")
                        if not isinstance(category, str): category = str(category)
                        
                        info_text = rule_info_data.get("info", "") # Default to empty string if missing or not string
                        if not isinstance(info_text, str): info_text = str(info_text)

                        current_pax_rule_details.append({
                            "category_name": category.replace("_", " ").title(), # e.g., "RULE_APPLICATION" -> "Rule Application"
                            "rules_text": info_text.strip()
                        })
                
                if current_pax_rule_details: # Only add if there are rule details for this pax type
                    current_route_pax_rules.append({
                        "pax_type": pax_type,
                        "fare_basis_code": fare_basis_code,
                        "rule_details": current_pax_rule_details
                    })
        
        if current_route_pax_rules: # Only add route if it has any processed passenger-specific rules
            adapted_route_rules_list.append({
                "route": route_str,
                "pax_specific_rules": current_route_pax_rules
            })

    return adapted_route_rules_list

# --- Example Usage (for direct testing of this adapter) ---
if __name__ == '__main__':
    sample_bdfare_fare_rules_response = {
      "message": None,
      "requestedOn": "2025-05-19T15:28:01.1628414Z",
      "respondedOn": "2025-05-19T15:28:01.1776609Z",
      "response": {
        "fareRuleRouteInfos": [
          {
            "route": "DAC→JSR",
            "fareRulePaxInfos": [
              {
                "paxType": "Adult",
                "fareBasisCode": "EDOMO",
                "fareRuleInfos": [
                  {
                    "category": "RULE_APPLICATION",
                    "info": "APPLICATION AND OTHER CONDITIONS\nRULE - 302/BD02\nUNLESS OTHERWISE SPECIFIED..." # Truncated for brevity
                  },
                  {
                    "category": "FLIGHT_APPLICATION",
                    "info": "FLIGHT APPLICATION\nUNLESS OTHERWISE SPECIFIED\n  THE FARE COMPONENT MUST BE ON..." # Truncated
                  },
                  {
                    "category": "ADVANCE_RESERVATIONS_TICKETING",
                    "info": "ADVANCE RES/TICKETING\nUNLESS OTHERWISE SPECIFIED\n  RESERVATIONS FOR ALL SECTORS ARE REQUIRED..." # Truncated
                  },
                  { # Example of a rule category with potentially short info
                    "category": "MAXIMUM_STAY",
                    "info": "MAXIMUM STAY\nNONE FOR ONE WAY FARES"
                  },
                  {
                    "category": "PENALTIES",
                    "info": "PENALTIES\nUNLESS OTHERWISE SPECIFIED\n  CHANGES\n    PER TICKET CHARGE BDT 1200 FOR REISSUE.\n  CANCELLATIONS\n    PER TICKET CHARGE BDT 1500 FOR REFUND." # Highly Truncated
                  }
                ]
              },
              { # Example for another pax type on the same route (if API supports)
                "paxType": "Child",
                "fareBasisCode": "CDOMO",
                "fareRuleInfos": [
                  {
                    "category": "CHILDREN_DISCOUNTS",
                    "info": "CHILDREN DISCOUNTS\nUNLESS OTHERWISE SPECIFIED\n  ACCOMPANIED CHILD 2-11 - CHARGE 75 PERCENT OF THE FARE."
                  }
                ]
              }
            ]
          },
          { # Example of another route (if API supports multiple routes in one response for fare rules)
            "route": "JSR→DAC",
            "fareRulePaxInfos": [
                {
                    "paxType": "Adult",
                    "fareBasisCode": "EDOMO",
                    "fareRuleInfos": [
                        {"category": "RETURN_JOURNEY_RULES", "info": "Return journey rules apply..."}
                    ]
                }
            ]
          }
        ],
        "error": None,
        "traceId": "80969b97-38a7-4f05-8253-b3cd4598aa5d"
      },
      "statusCode": "OK",
      "success": True,
      "error": None,
      "info": None
    }

    print("--- Adapting Sample BDFare Fare Rules Response (Based on User Example) ---")
    adapted_rules = adapt_bdfare_fare_rules(sample_bdfare_fare_rules_response)
    
    import json
    print(json.dumps(adapted_rules, indent=2))

    print("\n--- Adapting Response where 'success' is false ---")
    failed_success_response = {
      "message": "Authentication failed",
      "requestedOn": "2025-05-19T15:30:00.000Z",
      "respondedOn": "2025-05-19T15:30:00.100Z",
      "response": None,
      "statusCode": "Unauthorized",
      "success": False,
      "error": {"code": "401", "details": "Invalid API Key"},
      "info": None
    }
    adapted_failed_rules = adapt_bdfare_fare_rules(failed_success_response)
    print(json.dumps(adapted_failed_rules, indent=2)) # Expected: []

    print("\n--- Adapting Response with empty fareRuleRouteInfos ---")
    empty_routes_response = {
      "message": None, "requestedOn": "...", "respondedOn": "...",
      "response": {"fareRuleRouteInfos": [], "error": None, "traceId": "..."},
      "statusCode": "OK", "success": True, "error": None, "info": None
    }
    adapted_empty_routes = adapt_bdfare_fare_rules(empty_routes_response)
    print(json.dumps(adapted_empty_routes, indent=2)) # Expected: []