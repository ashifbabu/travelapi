from typing import Dict, Any
import logging
from app.flight_services.models.combined.combined_search import (
    FlightSearchResponse,
    FlightSegment,
    PriceDetails,
    BaggageDetails,
)

# Logger setup
logger = logging.getLogger("payload_conversion")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
def convert_to_bdfare_request(payload: dict) -> dict:
    """
    Convert Unified Data Model (UDM) payload to BDFare-specific request format.

    Args:
        payload (dict): Input payload in UDM format.

    Returns:
        dict: Transformed payload for BDFare API.

    Raises:
        ValueError: If required keys are missing in the payload.
    """
    try:
        return {
            "PointOfSale": payload["pointOfSale"],
            "Request": {
                "OriginDest": [
                    {
                        "OriginDepRequest": {
                            "IATA_LocationCode": origin["originDepRequest"]["iatA_LocationCode"],
                            "Date": origin["originDepRequest"]["date"]
                        },
                        "DestArrivalRequest": {
                            "IATA_LocationCode": origin["destArrivalRequest"]["iatA_LocationCode"]
                        }
                    }
                    for origin in payload["request"]["originDest"]
                ],
                "Pax": [
                    {
                        "PaxID": pax["paxID"],
                        "PTC": pax["ptc"]
                    }
                    for pax in payload["request"]["pax"]
                ],
                "ShoppingCriteria": {
                    "TripType": payload["request"]["shoppingCriteria"]["tripType"],
                    "TravelPreferences": payload["request"]["shoppingCriteria"]["travelPreferences"],
                    "ReturnUPSellInfo": payload["request"]["shoppingCriteria"]["returnUPSellInfo"]
                }
            }
        }
    except KeyError as e:
        raise ValueError(f"Missing key in payload: {e}")


def convert_bdfare_to_flyhub(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert BDFare request format to FlyHub request format."""
    trip_type = payload["shoppingCriteria"]["tripType"].lower()
    journey_type = "1" if trip_type == "oneway" else "2" if trip_type == "return" else "3"

    return {
        "AdultQuantity": sum(1 for pax in payload.get("pax", []) if pax.get("ptc") == "ADT"),
        "ChildQuantity": sum(1 for pax in payload.get("pax", []) if pax.get("ptc") == "CHD"),
        "InfantQuantity": sum(1 for pax in payload.get("pax", []) if pax.get("ptc") == "INF"),
        "EndUserIp": "103.124.251.147",  # Replace with dynamic IP if needed
        "JourneyType": journey_type,
        "Segments": [
            {
                "Origin": segment["originDepRequest"]["iatA_LocationCode"],
                "Destination": segment["destArrivalRequest"]["iatA_LocationCode"],
                "CabinClass": "1" if payload["shoppingCriteria"]["travelPreferences"]["cabinCode"].lower() == "economy" else "2",
                "DepartureDateTime": segment["originDepRequest"]["date"]
            }
            for segment in payload.get("originDest", [])
        ]
    }



def simplify_bdfare_response(bdfare_response: dict) -> list[FlightSegment]:
    """
    Simplify the BDFare API response to match the Unified Data Model.
    """
    simplified_segments = []
    for offer in bdfare_response.get("response", {}).get("offersGroup", []):
        for pax_segment_item in offer.get("offer", {}).get("paxSegmentList", []):
            pax_segment = pax_segment_item.get("paxSegment", {})
            simplified_segment = FlightSegment(
                from_=pax_segment["departure"]["iatA_LocationCode"],  # Maps to `from_`
                fromAirportName=pax_segment["departure"].get("airportName"),
                to=pax_segment["arrival"]["iatA_LocationCode"],
                toAirportName=pax_segment["arrival"].get("airportName"),
                departureTime=pax_segment["departure"]["aircraftScheduledDateTime"],
                arrivalTime=pax_segment["arrival"]["aircraftScheduledDateTime"],
                airlineCode=pax_segment["marketingCarrierInfo"]["carrierDesigCode"],
                airlineName=pax_segment["marketingCarrierInfo"]["carrierName"],
                flightNumber=pax_segment["flightNumber"],
                cabinClass=pax_segment["cabinType"],
                durationMinutes=pax_segment["duration"],
            )
            simplified_segments.append(simplified_segment)
    return simplified_segments
