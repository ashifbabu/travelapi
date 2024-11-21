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

