import subprocess
import json
from fastapi import APIRouter, HTTPException
import httpx
import asyncio
import os

router = APIRouter()

# Load API credentials from environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")
FLYHUB_BASE_URL = os.getenv("FLYHUB_PRODUCTION_URL")
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")

# Cached token for FlyHub
cached_token = {"token": None, "expires_at": 0}


async def fetch_bdfare_flights(payload):
    """Call BDFare API for flight searching with curl fallback."""
    url = f"{BDFARE_BASE_URL}/AirShopping"
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception:
        # Fallback to curl
        payload_json = json.dumps(payload)
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", f"X-API-KEY: {BDFARE_API_KEY}",
            "-H", "Content-Type: application/json",
            "-d", payload_json
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to decode JSON response from curl: {result.stdout}"
            )


async def fetch_flyhub_flights(payload):
    """Call FlyHub API for flight searching with curl fallback."""
    global cached_token
    if not cached_token["token"] or cached_token["expires_at"] <= asyncio.get_event_loop().time():
        await authenticate_flyhub()

    url = f"{FLYHUB_BASE_URL}AirSearch"
    headers = {
        "Authorization": f"Bearer {cached_token['token']}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception:
        # Fallback to curl
        payload_json = json.dumps(payload)
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", f"Authorization: Bearer {cached_token['token']}",
            "-H", "Content-Type: application/json",
            "-d", payload_json
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to decode JSON response from curl: {result.stdout}"
            )


async def authenticate_flyhub():
    """Authenticate with FlyHub and cache the token."""
    global cached_token
    url = f"{FLYHUB_BASE_URL}Authenticate"
    payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            token_data = response.json()
            cached_token["token"] = token_data["TokenId"]
            # Assume token validity is 1 hour
            cached_token["expires_at"] = asyncio.get_event_loop().time() + 3600
        else:
            raise HTTPException(status_code=response.status_code, detail="FlyHub Authentication Failed")
    except Exception:
        # Fallback to curl for authentication
        payload_json = json.dumps(payload)
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", "Content-Type: application/json",
            "-d", payload_json
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )
        try:
            token_data = json.loads(result.stdout)
            cached_token["token"] = token_data["TokenId"]
            cached_token["expires_at"] = asyncio.get_event_loop().time() + 3600
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to decode JSON response from curl: {result.stdout}"
            )


def convert_bdfare_to_flyhub(payload):
    """Convert BDFare request format to FlyHub request format."""
    trip_type = payload["request"]["shoppingCriteria"]["tripType"].lower()
    journey_type = "1" if trip_type == "oneway" else "2" if trip_type == "return" else "3"

    flyhub_payload = {
        "AdultQuantity": sum(1 for pax in payload.get("request", {}).get("pax", []) if pax.get("ptc") == "ADT"),
        "ChildQuantity": sum(1 for pax in payload.get("request", {}).get("pax", []) if pax.get("ptc") == "CHD"),
        "InfantQuantity": sum(1 for pax in payload.get("request", {}).get("pax", []) if pax.get("ptc") == "INF"),
        "EndUserIp": "103.124.251.147",  # Replace with actual IP if needed
        "JourneyType": journey_type,
        "Segments": [
            {
                "Origin": segment["originDepRequest"]["iatA_LocationCode"],
                "Destination": segment["destArrivalRequest"]["iatA_LocationCode"],
                "CabinClass": "1" if payload["request"]["shoppingCriteria"]["travelPreferences"]["cabinCode"].lower() == "economy" else "2",
                "DepartureDateTime": segment["originDepRequest"]["date"]
            }
            for segment in payload["request"]["originDest"]
        ]
    }
    return flyhub_payload


def simplify_bdfare_response(bdfare_response):
    """Simplify BDFare response for frontend integration."""
    simplified_offers = []

    for offer_group in bdfare_response.get('response', {}).get('offersGroup', []):
        offer = offer_group.get('offer', {})

        # Initialize simplified offer structure
        simplified_offer = {
            'id': offer.get('offerId'),
            'airline': offer.get('validatingCarrier'),
            'refundable': offer.get('refundable'),
            'fareType': offer.get('fareType'),
            'price': {},
            'segments': [],
            'baggageAllowance': [],
            'seatsRemaining': offer.get('seatsRemaining'),
        }

        # Process segments
        for pax_segment in offer.get('paxSegmentList', []):
            segment = pax_segment.get('paxSegment', {})
            simplified_segment = {
                'from': segment.get('departure', {}).get('iatA_LocationCode'),
                'to': segment.get('arrival', {}).get('iatA_LocationCode'),
                'departureTime': segment.get('departure', {}).get('aircraftScheduledDateTime'),
                'arrivalTime': segment.get('arrival', {}).get('aircraftScheduledDateTime'),
                'airlineCode': segment.get('marketingCarrierInfo', {}).get('carrierDesigCode'),
                'flightNumber': segment.get('flightNumber'),
                'cabinClass': segment.get('cabinType'),
                'durationMinutes': segment.get('duration'),
            }
            simplified_offer['segments'].append(simplified_segment)

        # Process fare details
        total_base_fare = 0
        total_tax = 0
        total_discount = 0
        currency = 'BDT'
        for fare_detail_item in offer.get('fareDetailList', []):
            fare_detail = fare_detail_item.get('fareDetail', {})
            total_base_fare += fare_detail.get('baseFare', 0)
            total_tax += fare_detail.get('tax', 0)
            total_discount += fare_detail.get('discount', 0)
            currency = fare_detail.get('currency', 'BDT')

        # Calculate total price
        total_price = total_base_fare + total_tax - total_discount
        simplified_offer['price'] = {
            'baseFare': total_base_fare,
            'tax': total_tax,
            'discount': total_discount,
            'total': total_price,
            'currency': currency,
        }

        # Process baggage allowance
        for baggage_item in offer.get('baggageAllowanceList', []):
            baggage = baggage_item.get('baggageAllowance', {})
            simplified_baggage = {
                'from': baggage.get('departure'),
                'to': baggage.get('arrival'),
                'checkIn': baggage.get('checkIn', []),
                'cabin': baggage.get('cabin', []),
            }
            simplified_offer['baggageAllowance'].append(simplified_baggage)

        # Append to simplified offers
        simplified_offers.append(simplified_offer)

    return simplified_offers



def simplify_flyhub_response(flyhub_response):
    """Simplify FlyHub response for frontend integration."""
    simplified_results = []
    
    for result in flyhub_response.get('Results', []):
        # Initialize the simplified result structure
        simplified_result = {
            'id': result.get('ResultID'),
            'airline': result.get('Validatingcarrier'),
            'refundable': result.get('IsRefundable'),
            'fareType': result.get('FareType'),
            'price': {},
            'segments': [],
            'baggageAllowance': [],
            'seatsRemaining': result.get('Availabilty'),
        }

        # Process segments
        for segment in result.get('segments', []):
            simplified_segment = {
                'from': segment.get('Origin', {}).get('Airport', {}).get('AirportCode'),
                'to': segment.get('Destination', {}).get('Airport', {}).get('AirportCode'),
                'departureTime': segment.get('Origin', {}).get('DepTime'),
                'arrivalTime': segment.get('Destination', {}).get('ArrTime'),
                'airlineCode': segment.get('Airline', {}).get('AirlineCode'),
                'flightNumber': segment.get('Airline', {}).get('FlightNumber'),
                'cabinClass': segment.get('Airline', {}).get('CabinClass'),
                'durationMinutes': segment.get('JourneyDuration'),
            }
            simplified_result['segments'].append(simplified_segment)

            # Process baggage allowance for each segment
            for baggage in segment.get('baggageDetails', []):
                simplified_baggage = {
                    'departure': segment.get('Origin', {}).get('Airport', {}).get('AirportCode'),
                    'arrival': segment.get('Destination', {}).get('Airport', {}).get('AirportCode'),
                    'checkIn': baggage.get('Checkin'),
                    'cabin': baggage.get('Cabin'),
                    'paxType': baggage.get('PaxType'),
                }
                simplified_result['baggageAllowance'].append(simplified_baggage)

        # Process fare details
        total_base_fare = 0
        total_tax = 0
        total_discount = 0
        currency = None
        for fare in result.get('Fares', []):
            total_base_fare += fare.get('BaseFare', 0)
            total_tax += fare.get('Tax', 0)
            total_discount += fare.get('Discount', 0)
            currency = fare.get('Currency', 'BDT')

        # Calculate total price
        total_price = total_base_fare + total_tax - total_discount
        simplified_result['price'] = {
            'baseFare': total_base_fare,
            'tax': total_tax,
            'discount': total_discount,
            'total': total_price,
            'currency': currency,
        }

        # Add the simplified result to the list
        simplified_results.append(simplified_result)

    return simplified_results



@router.post("/search")
async def combined_search(payload: dict):
    """
    Perform a combined flight search using BDFare and FlyHub APIs.

    Args:
        payload (dict): The flight search request payload in BDFare format.

    Returns:
        dict: Simplified combined flight results from BDFare and FlyHub.
    """
    flyhub_payload = convert_bdfare_to_flyhub(payload)

    try:
        bdfare_task = fetch_bdfare_flights(payload)
        flyhub_task = fetch_flyhub_flights(flyhub_payload)

        bdfare_response, flyhub_response = await asyncio.gather(bdfare_task, flyhub_task)

        # Simplify responses
        simplified_bdfare = simplify_bdfare_response(bdfare_response)
        simplified_flyhub = simplify_flyhub_response(flyhub_response)

        combined_results = {
            "bdfare": simplified_bdfare,
            "flyhub": simplified_flyhub
        }

        return combined_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
