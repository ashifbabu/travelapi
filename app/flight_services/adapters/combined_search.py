

from app.flight_services.services.ailineLogoService import get_airline_by_id
def format_flight_data_with_ids(data):
    flights = []

       # Process bdfare
    if "bdfare" in data and data["bdfare"].get("response"):
        trace_id = data["bdfare"]["response"].get("traceId", "N/A")
        offers_group = data["bdfare"]["response"].get("offersGroup", [])
        special_offers_group = data["bdfare"]["response"].get("specialReturnOffersGroup", {})

        def process_offer_group(offer_group, source_label):
            for offer_group_item in offer_group.get("ob", []) + offer_group.get("ib", []):
                offer = offer_group_item.get("offer", {})
                fare_details = offer.get("fareDetailList", [])
                pax_segments = offer.get("paxSegmentList", [])
                baggage_list = offer.get("baggageAllowanceList", [])

                # Process segments
                segments = []
                for segment_item in pax_segments:
                    pax_segment = segment_item.get("paxSegment", {})
                    airline_code = pax_segment.get('marketingCarrierInfo', {}).get('carrierDesigCode', 'Unknown')
                    airline_data = get_airline_by_id(airline_code)  # Use the function to get airline data
                    airline_logo = airline_data['logo'] if airline_data else 'Logo not available'
                   
                    segments.append({
                        "From": {
                            "Code": pax_segment.get("departure", {}).get("iatA_LocationCode", ""),
                            "Name": pax_segment.get("departure", {}).get("terminalName", ""),
                            "DepartureTime": pax_segment.get("departure", {}).get("aircraftScheduledDateTime", "")
                        },
                        "To": {
                            "Code": pax_segment.get("arrival", {}).get("iatA_LocationCode", ""),
                            "Name": pax_segment.get("arrival", {}).get("terminalName", ""),
                            "ArrivalTime": pax_segment.get("arrival", {}).get("aircraftScheduledDateTime", "")
                        },
 "Airline": {
            "Name": pax_segment.get('marketingCarrierInfo', {}).get('carrierName', 'Unknown'),
             "Code": airline_code,
                            "Logo": airline_logo 
        },                        "FlightNumber": pax_segment.get("flightNumber", "Unknown"),
                        "CabinClass": pax_segment.get("cabinType", "Unknown"),
                        "Duration": f"{pax_segment.get('duration', 0)} minutes"
                    })

                # Process pricing
                pricing = []
                for fare_detail in fare_details:
                    fare = fare_detail.get("fareDetail", {})
                    pricing.append({
                        "PaxType": fare.get("paxType", "Unknown"),
                        "Currency": fare.get("currency", "Unknown"),
                        "BaseFare": fare.get("baseFare", 0),
                        "Tax": fare.get("tax", 0),
                        "OtherFee": fare.get("otherFee", 0),
                        "Discount": fare.get("discount", 0),
                        "VAT": fare.get("vat", 0),
                        "Total": fare.get("subTotal", 0)
                    })

                # Process baggage
                baggage = []
                for baggage_item in baggage_list:
                    baggage_data = baggage_item.get("baggageAllowance", {})
                    baggage.append({
                        "From": baggage_data.get("departure", "Unknown"),
                        "To": baggage_data.get("arrival", "Unknown"),
                        "CheckIn": baggage_data.get("checkIn", "Not Available"),
                        "Cabin": baggage_data.get("cabin", "Not Available")
                    })

                flights.append({
                    "Source": source_label,
                    "TraceId": trace_id,
                    "OfferId": offer.get("offerId", "Unknown"),
                    "Segments": segments,
                    "Pricing": pricing,
                    "BaggageAllowance": baggage,
                    "Refundable": offer.get("refundable", False),
                    "FareType": offer.get("fareType", "Unknown"),
                    "SeatsRemaining": int(offer.get("seatsRemaining", 0))
                })

        if offers_group:  # Ensure offersGroup is not None
            process_offer_group({"ob": offers_group}, "bdfare")

        if special_offers_group:  # Process special offers group under the same source label "bdfare"
            process_offer_group(special_offers_group, "bdfare")

    # Process flyhub
    if "flyhub" in data and data["flyhub"].get("Results"):
        search_id = data["flyhub"].get("SearchId", "N/A")
        for result in data["flyhub"]["Results"]:
            segment_groups = {}

            # Group segments by SegmentGroup
            for segment in result.get("segments", []):
                group = segment.get("SegmentGroup", 0)
                if group not in segment_groups:
                    segment_groups[group] = []
                segment_groups[group].append(segment)

            grouped_segments = []
            for group_id, segments in segment_groups.items():
                grouped_segments.append({
                    "GroupId": group_id,
                    "Segments": [
                        {
                            "From": {
                                "Code": seg.get("Origin", {}).get("Airport", {}).get("AirportCode", "Unknown"),
                                "Name": seg.get("Origin", {}).get("Airport", {}).get("AirportName", "Unknown"),
                                "DepartureTime": seg.get("Origin", {}).get("DepTime", "Unknown")
                            },
                            "To": {
                                "Code": seg.get("Destination", {}).get("Airport", {}).get("AirportCode", "Unknown"),
                                "Name": seg.get("Destination", {}).get("Airport", {}).get("AirportName", "Unknown"),
                                "ArrivalTime": seg.get("Destination", {}).get("ArrTime", "Unknown")
                            },
"Airline": {
                    "Name": seg.get('Airline', {}).get('AirlineName', 'Unknown'),
                    "Code": seg.get('Airline', {}).get('AirlineCode', 'Unknown'),
                     "Logo": get_airline_by_id(seg.get('Airline', {}).get('AirlineCode', 'Unknown'))['logo']
                },                            "FlightNumber": seg.get("Airline", {}).get("FlightNumber", "Unknown"),
                            "CabinClass": seg.get("Airline", {}).get("CabinClass", "Unknown"),
                            "Duration": f"{seg.get('JourneyDuration', 0)} minutes",
                            "Baggage": seg.get("baggageDetails", [{}])[0].get("Checkin", "Not Available") if seg.get("baggageDetails") else "Not Available"
                        }
                        for seg in segments
                    ]
                })

            flights.append({
                "Source": "flyhub",
                "SearchId": search_id,
                "ResultId": result.get("ResultID", "Unknown"),
                "ValidatingCarrier": result.get("Validatingcarrier", "N/A"),
                "Refundable": result.get("IsRefundable", False),
                "FareType": result.get("FareType", "Unknown"),
                "Pricing": {
                    "Currency": result.get("Fares", [{}])[0].get("Currency", "Unknown"),
                    "BaseFare": result.get("Fares", [{}])[0].get("BaseFare", 0),
                    "Tax": result.get("Fares", [{}])[0].get("Tax", 0),
                    "Discount": result.get("Fares", [{}])[0].get("Discount", 0),
                    "TotalFare": result.get("TotalFare", 0)
                },
                "Availability": result.get("Availabilty", 0),
                "Segments": grouped_segments
            })

    return {"Flights": flights}
