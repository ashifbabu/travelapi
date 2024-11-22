import requests

def convert_bdfare_to_flyhub(payload):
    """Convert BDFare request format to FlyHub request format."""
    trip_type = payload["request"]["shoppingCriteria"]["tripType"].lower()
    journey_type = "1" if trip_type == "Oneway" else "2" if trip_type == "Return" else "3"

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
    airport_name_cache = {}  # Cache for airport names to avoid redundant API calls

    for offer_group in bdfare_response.get('response', {}).get('offersGroup', []):
        offer = offer_group.get('offer', {})

        # Initialize simplified offer structure
        simplified_offer = {
            'id': offer.get('offerId'),
            'airline': offer.get('validatingCarrier'),
            'airlineName': offer.get('paxSegmentList', [{}])[0].get('paxSegment', {}).get('marketingCarrierInfo', {}).get('carrierName', None),
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
            departure_info = segment.get('departure', {})
            arrival_info = segment.get('arrival', {})

            # Get from and to IATA codes
            from_iata = departure_info.get('iatA_LocationCode')
            to_iata = arrival_info.get('iatA_LocationCode')

            # Get airport names, use cache to avoid redundant API calls
            # Fetch 'fromAirportName'
            from_airport_name = departure_info.get('airportName')
            if not from_airport_name:
                if from_iata in airport_name_cache:
                    from_airport_name = airport_name_cache[from_iata]
                else:
                    # Fetch from API
                    try:
                        response = requests.get(f'https://port-api.com/port/code/{from_iata}', headers={'accept': 'application/json'})
                        if response.status_code == 200:
                            data = response.json()
                            if data['features']:
                                from_airport_name = data['features'][0]['properties']['name']
                                airport_name_cache[from_iata] = from_airport_name
                            else:
                                from_airport_name = "Unknown Departure Airport"
                                airport_name_cache[from_iata] = from_airport_name
                        else:
                            from_airport_name = "Unknown Departure Airport"
                    except Exception:
                        from_airport_name = "Unknown Departure Airport"

            # Fetch 'toAirportName'
            to_airport_name = arrival_info.get('airportName')
            if not to_airport_name:
                if to_iata in airport_name_cache:
                    to_airport_name = airport_name_cache[to_iata]
                else:
                    # Fetch from API
                    try:
                        response = requests.get(f'https://port-api.com/port/code/{to_iata}', headers={'accept': 'application/json'})
                        if response.status_code == 200:
                            data = response.json()
                            if data['features']:
                                to_airport_name = data['features'][0]['properties']['name']
                                airport_name_cache[to_iata] = to_airport_name
                            else:
                                to_airport_name = "Unknown Arrival Airport"
                                airport_name_cache[to_iata] = to_airport_name
                        else:
                            to_airport_name = "Unknown Arrival Airport"
                    except Exception:
                        to_airport_name = "Unknown Arrival Airport"

            simplified_segment = {
                'from': from_iata,
                'fromAirportName': from_airport_name,
                'to': to_iata,
                'toAirportName': to_airport_name,
                'departureTime': departure_info.get('aircraftScheduledDateTime'),
                'arrivalTime': arrival_info.get('aircraftScheduledDateTime'),
                'airlineCode': segment.get('marketingCarrierInfo', {}).get('carrierDesigCode'),
                'airlineName': segment.get('marketingCarrierInfo', {}).get('carrierName'),  # Airline name for the segment
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
                'checkIn': [
                    {
                        'paxType': check_in.get('paxType'),
                        'allowance': check_in.get('allowance')
                    }
                    for check_in in baggage.get('checkIn', [])
                ],
                'cabin': [
                    {
                        'paxType': cabin.get('paxType'),
                        'allowance': cabin.get('allowance')
                    }
                    for cabin in baggage.get('cabin', [])
                ],
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
            'airlineName': result.get('ValidatingcarrierName'),  # Added airline name
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
                'fromAirportName': segment.get('Origin', {}).get('Airport', {}).get('AirportName'),  # Added departure airport name
                'to': segment.get('Destination', {}).get('Airport', {}).get('AirportCode'),
                'toAirportName': segment.get('Destination', {}).get('Airport', {}).get('AirportName'),  # Added arrival airport name
                'departureTime': segment.get('Origin', {}).get('DepTime'),
                'arrivalTime': segment.get('Destination', {}).get('ArrTime'),
                'airlineCode': segment.get('Airline', {}).get('AirlineCode'),
                'airlineName': segment.get('Airline', {}).get('AirlineName'),  # Added airline name for the segment
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
