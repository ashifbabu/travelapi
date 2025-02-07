# import pandas as pd
# import json
# import logging
# from app.flight_services.services.ailineLogoService import get_airline_by_id

# # ✅ Configure logging
# logger = logging.getLogger("format_flight_data")
# logger.setLevel(logging.INFO)
# handler = logging.StreamHandler()
# formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# # ✅ Load airport data from a JSON file into a DataFrame
# with open('app/flight_services/data/airports.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)
# airports_df = pd.json_normalize(data)
# airports_df.rename(columns={
#     'IATA': 'iata_code',
#     'Airport name': 'airport_name',
#     'City': 'city',
#     'Country': 'country'
# }, inplace=True)
# airports_df.dropna(subset=['iata_code'], inplace=True)

# # ✅ Function to get airport name by IATA code
# def get_airport_name_by_code(iata_code):
#     logger.info(f"Fetching airport name for IATA code: {iata_code}")
#     if airports_df is not None:
#         result = airports_df.loc[airports_df['iata_code'].str.upper() == iata_code.upper(), 'airport_name']
#         if not result.empty:
#             airport_name = result.values[0]
#             logger.info(f"Found airport name: {airport_name} for IATA code: {iata_code}")
#             return airport_name
#     logger.warning(f"Airport name not found for IATA code: {iata_code}")
#     return "Unknown Airport"

# # ✅ Function to format flight data
# def format_flight_data_with_ids(data):
#     flights = []

#     # ✅ Process BDFare data
#     if "bdfare" in data and data["bdfare"].get("response"):
#         trace_id = data["bdfare"]["response"].get("traceId", "N/A")
#         offers_group = data["bdfare"]["response"].get("offersGroup", [])
#         special_offers_group = data["bdfare"]["response"].get("specialReturnOffersGroup", {})

#         def process_offer_group(offer_group, source_label):
#             for offer_group_item in offer_group.get("ob", []) + offer_group.get("ib", []):
#                 offer = offer_group_item.get("offer", {})
#                 fare_details = offer.get("fareDetailList", [])
#                 pax_segments = offer.get("paxSegmentList", [])
#                 baggage_list = offer.get("baggageAllowanceList", [])

#                 # ✅ Process segments
#                 segments = []
#                 for segment_item in pax_segments:
#                     pax_segment = segment_item.get("paxSegment", {})
#                     departure_code = pax_segment.get("departure", {}).get("iatA_LocationCode", "")
#                     arrival_code = pax_segment.get("arrival", {}).get("iatA_LocationCode", "")
#                     departure_name = get_airport_name_by_code(departure_code)
#                     arrival_name = get_airport_name_by_code(arrival_code)
#                     airline_code = pax_segment.get('marketingCarrierInfo', {}).get('carrierDesigCode', 'Unknown')
#                     airline_data = get_airline_by_id(airline_code)
#                     airline_logo = airline_data['logo'] if airline_data else 'Logo not available'

#                     segments.append({
#                         "From": {
#                             "Code": departure_code,
#                             "Name": departure_name,
#                             "DepartureTime": pax_segment.get("departure", {}).get("aircraftScheduledDateTime", "")
#                         },
#                         "To": {
#                             "Code": arrival_code,
#                             "Name": arrival_name,
#                             "ArrivalTime": pax_segment.get("arrival", {}).get("aircraftScheduledDateTime", "")
#                         },
#                         "Airline": {
#                             "Name": pax_segment.get('marketingCarrierInfo', {}).get('carrierName', 'Unknown'),
#                             "Code": airline_code,
#                             "Logo": airline_logo
#                         },
#                         "FlightNumber": pax_segment.get("flightNumber", "Unknown"),
#                         "CabinClass": pax_segment.get("cabinType", "Unknown"),
#                         "Duration": f"{pax_segment.get('duration', 0)} minutes"
#                     })

#                 # ✅ Process pricing
#                 pricing = []
#                 for fare_detail in fare_details:
#                     fare = fare_detail.get("fareDetail", {})
#                     pricing.append({
#                         "PaxType": fare.get("paxType", "Unknown"),
#                         "Currency": fare.get("currency", "Unknown"),
#                         "BaseFare": fare.get("baseFare", 0),
#                         "Tax": fare.get("tax", 0),
#                         "OtherFee": fare.get("otherFee", 0),
#                         "Discount": fare.get("discount", 0),
#                         "VAT": fare.get("vat", 0),
#                         "Total": fare.get("subTotal", 0)
#                     })

#                 # ✅ Process baggage
#                 baggage = []
#                 for baggage_item in baggage_list:
#                     baggage_data = baggage_item.get("baggageAllowance", {})
#                     baggage.append({
#                         "From": baggage_data.get("departure", "Unknown"),
#                         "To": baggage_data.get("arrival", "Unknown"),
#                         "CheckIn": baggage_data.get("checkIn", "Not Available"),
#                         "Cabin": baggage_data.get("cabin", "Not Available")
#                     })

#                 # ✅ Add flight data
#                 flights.append({
#                     "Source": source_label,
#                     "TraceId": trace_id,
#                     "OfferId": offer.get("offerId", "Unknown"),
#                     "Segments": segments,
#                     "Pricing": pricing,
#                     "BaggageAllowance": baggage,
#                     "Refundable": offer.get("refundable", False),
#                     "FareType": offer.get("fareType", "Unknown"),
#                     "SeatsRemaining": int(offer.get("seatsRemaining", 0))
#                 })

#         # Process BDFare offers
#         if offers_group:
#             process_offer_group({"ob": offers_group}, "bdfare")

#         # Process special offers group
#         if special_offers_group:
#             process_offer_group(special_offers_group, "bdfare")

#     # ✅ Process FlyHub data
#     if "flyhub" in data and data["flyhub"].get("Results"):
#         search_id = data["flyhub"].get("SearchId", "N/A")
#         for result in data["flyhub"]["Results"]:
#             segment_groups = {}
#             for segment in result.get("segments", []):
#                 group = segment.get("SegmentGroup", 0)
#                 if group not in segment_groups:
#                     segment_groups[group] = []
#                 segment_groups[group].append(segment)

#             grouped_segments = []
#             for group_id, segments in segment_groups.items():
#                 grouped_segments.append({
#                     "GroupId": group_id,
#                     "Segments": [
#                         {
#                             "From": {
#                                 "Code": seg.get("Origin", {}).get("Airport", {}).get("AirportCode", "Unknown"),
#                                 "Name": seg.get("Origin", {}).get("Airport", {}).get("AirportName", "Unknown"),
#                                 "DepartureTime": seg.get("Origin", {}).get("DepTime", "Unknown")
#                             },
#                             "To": {
#                                 "Code": seg.get("Destination", {}).get("Airport", {}).get("AirportCode", "Unknown"),
#                                 "Name": seg.get("Destination", {}).get("Airport", {}).get("AirportName", "Unknown"),
#                                 "ArrivalTime": seg.get("Destination", {}).get("ArrTime", "Unknown")
#                             },
#                             "Airline": {
#                                 "Name": seg.get("Airline", {}).get("AirlineName", "Unknown"),
#                                 "Code": seg.get("Airline", {}).get("AirlineCode", "Unknown"),
#                                 "Logo": get_airline_by_id(seg.get("Airline", {}).get("AirlineCode", "Unknown"))["logo"]
#                             },
#                             "FlightNumber": seg.get("Airline", {}).get("FlightNumber", "Unknown"),
#                             "CabinClass": seg.get("Airline", {}).get("CabinClass", "Unknown"),
#                             "Duration": f"{seg.get('JourneyDuration', 0)} minutes",
#                             "Baggage": (
#     seg.get("baggageDetails", [{}])[0].get("Checkin", "Not Available")
#     if seg.get("baggageDetails") and len(seg.get("baggageDetails")) > 0
#     else "Not Available"
# )

#                         }
#                         for seg in segments
#                     ]
#                 })

#             flights.append({
#                 "Source": "flyhub",
#                 "SearchId": search_id,
#                 "ResultId": result.get("ResultID", "Unknown"),
#                 "ValidatingCarrier": result.get("Validatingcarrier", "N/A"),
#                 "Refundable": result.get("IsRefundable", False),
#                 "FareType": result.get("FareType", "Unknown"),
#                 "Pricing": {
#                     "Currency": result.get("Fares", [{}])[0].get("Currency", "Unknown"),
#                     "BaseFare": result.get("Fares", [{}])[0].get("BaseFare", 0),
#                     "Tax": result.get("Fares", [{}])[0].get("Tax", 0),
#                     "Discount": result.get("Fares", [{}])[0].get("Discount", 0),
#                     "TotalFare": result.get("TotalFare", 0)
#                 },
#                 "Availability": result.get("Availabilty", 0),
#                 "Segments": grouped_segments
#             })

#     return {"Flights": flights}

import pandas as pd
import json
import logging
from app.flight_services.services.ailineLogoService import get_airline_by_id

# ------------------------------------------------------------------------------
# Configure logging
# ------------------------------------------------------------------------------
logger = logging.getLogger("format_flight_data")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# ------------------------------------------------------------------------------
# Load airport data from JSON file into a DataFrame
# ------------------------------------------------------------------------------
with open('app/flight_services/data/airports.json', 'r', encoding='utf-8') as file:
    airport_data = json.load(file)

airports_df = pd.json_normalize(airport_data)
airports_df.rename(columns={
    'IATA': 'iata_code',
    'Airport name': 'airport_name',
    'City': 'city',
    'Country': 'country'
}, inplace=True)
airports_df.dropna(subset=['iata_code'], inplace=True)

# ------------------------------------------------------------------------------
# Helper function: get airport name by IATA code
# ------------------------------------------------------------------------------
def get_airport_name_by_code(iata_code):
    logger.info(f"Fetching airport name for IATA code: {iata_code}")
    if airports_df is not None:
        result = airports_df.loc[airports_df['iata_code'].str.upper() == iata_code.upper(), 'airport_name']
        if not result.empty:
            airport_name = result.values[0]
            logger.info(f"Found airport name: {airport_name} for IATA code: {iata_code}")
            return airport_name
    logger.warning(f"Airport name not found for IATA code: {iata_code}")
    return "Unknown Airport"

# ------------------------------------------------------------------------------
# Helper function: process a single bdfare offer (all fields except IDs)
# ------------------------------------------------------------------------------
def process_bdfare_offer(offer):
    """
    Returns a dictionary containing all data from a bdfare offer,
    with unified key names. Now also includes the offerId.
    """
    result = {}
    # Capture offerId
    result["OfferId"] = offer.get("offerId")
    # Include twoOnewayIndex if present
    if "twoOnewayIndex" in offer:
        result["TwoOnewayIndex"] = offer.get("twoOnewayIndex")
    result["ValidatingCarrier"] = offer.get("validatingCarrier")
    result["Refundable"] = offer.get("refundable")
    result["FareType"] = offer.get("fareType")
    
    # --- Price breakdown (raw "price" object) ---
    if "price" in offer:
        price_raw = offer["price"]
        def fix_currency(obj):
            if isinstance(obj, dict) and "curreny" in obj:
                obj["currency"] = obj.pop("curreny")
            return obj
        result["PriceBreakdown"] = { key: fix_currency(value) for key, value in price_raw.items() }
    else:
        result["PriceBreakdown"] = {}
    
    # --- Fare details (from fareDetailList) ---
    fare_details = []
    for item in offer.get("fareDetailList", []):
        fare = item.get("fareDetail", {})
        fare_details.append({
            "BaseFare": fare.get("baseFare"),
            "Tax": fare.get("tax"),
            "OtherFee": fare.get("otherFee"),
            "Discount": fare.get("discount"),
            "VAT": fare.get("vat"),
            "Currency": fare.get("currency"),
            "PaxType": fare.get("paxType"),
            "PaxCount": fare.get("paxCount"),
            "SubTotal": fare.get("subTotal")
        })
    result["FareDetails"] = fare_details

    # --- Process segments from paxSegmentList ---
    segments = []
    for seg_item in offer.get("paxSegmentList", []):
        seg = seg_item.get("paxSegment", {})
        departure = seg.get("departure", {})
        arrival = seg.get("arrival", {})
        segment_obj = {
            "Departure": {
                "IATACode": departure.get("iatA_LocationCode"),
                "Terminal": departure.get("terminalName"),
                "ScheduledTime": departure.get("aircraftScheduledDateTime"),
                "AirportName": get_airport_name_by_code(departure.get("iatA_LocationCode"))
            },
            "Arrival": {
                "IATACode": arrival.get("iatA_LocationCode"),
                "Terminal": arrival.get("terminalName"),
                "ScheduledTime": arrival.get("aircraftScheduledDateTime"),
                "AirportName": get_airport_name_by_code(arrival.get("iatA_LocationCode"))
            },
            "MarketingCarrier": seg.get("marketingCarrierInfo", {}),
            "OperatingCarrier": seg.get("operatingCarrierInfo", {}),
            "AircraftType": seg.get("iatA_AircraftType", {}).get("iatA_AircraftTypeCode"),
            "RBD": seg.get("rbd"),
            "FlightNumber": seg.get("flightNumber"),
            "SegmentGroup": seg.get("segmentGroup"),
            "ReturnJourney": seg.get("returnJourney"),
            "AirlinePNR": seg.get("airlinePNR"),
            "TechnicalStopOver": seg.get("technicalStopOver"),
            "Duration": f"{seg.get('duration', '0')} minutes",
            "CabinType": seg.get("cabinType")
        }
        segments.append(segment_obj)
    result["Segments"] = segments

    # --- Process baggage allowances ---
    baggage_list = []
    for bag_item in offer.get("baggageAllowanceList", []):
        bag = bag_item.get("baggageAllowance", {})
        baggage_list.append({
            "Departure": bag.get("departure"),
            "Arrival": bag.get("arrival"),
            "CheckIn": bag.get("checkIn"),
            "Cabin": bag.get("cabin")
        })
    result["BaggageAllowance"] = baggage_list

    # --- Include upSellBrandList (if any) and seatsRemaining (as integer) ---
    result["UpSellBrandList"] = offer.get("upSellBrandList")
    try:
        result["SeatsRemaining"] = int(offer.get("seatsRemaining", 0))
    except Exception as e:
        result["SeatsRemaining"] = 0

    return result

# ------------------------------------------------------------------------------
# Helper function: process a single flyhub result (all fields except IDs)
# ------------------------------------------------------------------------------
def process_flyhub_result(result):
    """
    Returns a dictionary containing all data from a flyhub result,
    with unified key names. (Omitted: SearchId and ResultID will be added in main.)
    """
    flight = {}
    flight["Source"] = "flyhub"
    flight["IsRefundable"] = result.get("IsRefundable")
    flight["FareType"] = result.get("FareType")
    flight["Discount"] = result.get("Discount")
    flight["ValidatingCarrier"] = result.get("Validatingcarrier")
    flight["LastTicketDate"] = result.get("LastTicketDate")
    # --- Pricing: Process each fare in Fares ---
    fares = result.get("Fares", [])
    pricing = []
    for fare in fares:
        pricing.append({
            "BaseFare": fare.get("BaseFare"),
            "Tax": fare.get("Tax"),
            "Currency": fare.get("Currency"),
            "OtherCharges": fare.get("OtherCharges"),
            "Discount": fare.get("Discount"),
            "AgentMarkUp": fare.get("AgentMarkUp"),
            "PaxType": fare.get("PaxType"),
            "PassengerCount": fare.get("PassengerCount"),
            "ServiceFee": fare.get("ServiceFee")
        })
    flight["Pricing"] = pricing

    # --- Extra flyhub fields ---
    flight["TotalFare"] = result.get("TotalFare")
    flight["TotalFareWithAgentMarkup"] = result.get("TotalFareWithAgentMarkup")
    flight["Currency"] = result.get("Currency")
    flight["Availabilty"] = result.get("Availabilty")
    flight["isMiniRulesAvailable"] = result.get("isMiniRulesAvailable")
    flight["HoldAllowed"] = result.get("HoldAllowed")

    # --- Process segments: group by TripIndicator into Outbound and Inbound ---
    outbound_segments = []
    inbound_segments = []
    for seg in result.get("segments", []):
        seg_obj = {
            "Departure": {
                "IATACode": seg.get("Origin", {}).get("Airport", {}).get("AirportCode"),
                "AirportName": seg.get("Origin", {}).get("Airport", {}).get("AirportName"),
                "Terminal": seg.get("Origin", {}).get("Airport", {}).get("Terminal"),
                "ScheduledTime": seg.get("Origin", {}).get("DepTime")
            },
            "Arrival": {
                "IATACode": seg.get("Destination", {}).get("Airport", {}).get("AirportCode"),
                "AirportName": seg.get("Destination", {}).get("Airport", {}).get("AirportName"),
                "Terminal": seg.get("Destination", {}).get("Airport", {}).get("Terminal"),
                "ScheduledTime": seg.get("Destination", {}).get("ArrTime")
            },
            "Airline": {
                "Code": seg.get("Airline", {}).get("AirlineCode"),
                "Name": seg.get("Airline", {}).get("AirlineName"),
                "FlightNumber": seg.get("Airline", {}).get("FlightNumber"),
                "BookingClass": seg.get("Airline", {}).get("BookingClass"),
                "CabinClass": seg.get("Airline", {}).get("CabinClass"),
                "OperatingCarrier": seg.get("Airline", {}).get("OperatingCarrier"),
                "Logo": get_airline_by_id(seg.get("Airline", {}).get("AirlineCode", "Unknown")).get("logo", "Logo not available")
            },
            "JourneyDuration": f"{seg.get('JourneyDuration', '0')} minutes",
            "StopQuantity": seg.get("StopQuantity"),
            "Equipment": seg.get("Equipment"),
            "Baggage": seg.get("baggageDetails", [{}])[0].get("Checkin") if seg.get("baggageDetails") else None,
            "SegmentGroup": seg.get("SegmentGroup")
        }
        if seg.get("TripIndicator") == "OutBound":
            outbound_segments.append(seg_obj)
        elif seg.get("TripIndicator") == "InBound":
            inbound_segments.append(seg_obj)
        else:
            outbound_segments.append(seg_obj)  # fallback
    flight["OutboundSegments"] = outbound_segments
    flight["InboundSegments"] = inbound_segments

    return flight

# ------------------------------------------------------------------------------
# Main function: format_flight_data_with_ids
# ------------------------------------------------------------------------------
def format_flight_data_with_ids(data):
    """
    Processes raw flight response data from bdfare and flyhub and returns
    a unified structure that includes every piece of data (with the same naming)
    including IDs:
      - For bdfare: TraceId (once for the response) and each flight's OfferId.
      - For flyhub: SearchId (once for the response) and each flight's ResultID.
    For bdfare return flights, outbound and inbound offers are paired by index.
    """
    flights = []

    # --- Process bdfare data ---
    if "bdfare" in data and data["bdfare"].get("response"):
        bdfare_data = data["bdfare"]
        response = bdfare_data.get("response", {})
        # Include the overall TraceId from the bdfare response
        trace_id = response.get("traceId")
        # Create a metadata dictionary from the top-level bdfare data
        bdfare_meta = {
            "Message": bdfare_data.get("message"),
            "RequestedOn": bdfare_data.get("requestedOn"),
            "RespondedOn": bdfare_data.get("respondedOn"),
            "StatusCode": bdfare_data.get("statusCode"),
            "Success": bdfare_data.get("success"),
            "Error": bdfare_data.get("error"),
            "Info": bdfare_data.get("info"),
            "SpecialReturn": response.get("specialReturn"),
            "MoreOffersAvailableAirline": response.get("moreOffersAvailableAirline"),
            "TraceId": trace_id
        }
        # Process return flight offers from specialReturnOffersGroup
        if response.get("specialReturn") or response.get("specialReturnOffersGroup"):
            special_group = response.get("specialReturnOffersGroup", {})
            outbound_offers = []
            inbound_offers = []
            # Process offers from "ob" and assign them based on route
            ob_offers = special_group.get("ob", [])
            origin = None
            destination = None
            for idx, o in enumerate(ob_offers):
                processed = process_bdfare_offer(o.get("offer", {}))
                if processed["Segments"]:
                    first_seg = processed["Segments"][0]
                    # For the very first offer, assume it is outbound and record its route.
                    if origin is None and destination is None:
                        origin = first_seg["Departure"]["IATACode"]
                        destination = first_seg["Arrival"]["IATACode"]
                        outbound_offers.append(processed)
                    else:
                        # If the offer's first segment appears inverted, treat it as inbound.
                        if (first_seg["Departure"]["IATACode"] == destination and
                            first_seg["Arrival"]["IATACode"] == origin):
                            inbound_offers.append(processed)
                        else:
                            outbound_offers.append(processed)
            # Also process offers from "ib" (or fallback "inb")
            ib_offers = special_group.get("ib", [])
            if not ib_offers and special_group.get("inb"):
                ib_offers = special_group.get("inb", [])
            for o in ib_offers:
                processed = process_bdfare_offer(o.get("offer", {}))
                inbound_offers.append(processed)
            # Pair outbound and inbound offers by index
            num_pairs = min(len(outbound_offers), len(inbound_offers))
            for i in range(num_pairs):
                ob = outbound_offers[i]
                ib = inbound_offers[i]
                flight_obj = {
                    "Source": "bdfare",
                    "TraceId": trace_id,
                    "OfferIdOutbound": ob.get("OfferId"),
                    "OfferIdInbound": ib.get("OfferId"),
                    "ValidatingCarrier": ob.get("ValidatingCarrier") or ib.get("ValidatingCarrier"),
                    "Refundable": ob.get("Refundable") and ib.get("Refundable"),
                    "FareType": ob.get("FareType"),
                    "Pricing": {
                        "FareDetails": {"Outbound": ob.get("FareDetails"), "Inbound": ib.get("FareDetails")},
                        "PriceBreakdown": {"Outbound": ob.get("PriceBreakdown"), "Inbound": ib.get("PriceBreakdown")}
                    },
                    "OutboundSegments": ob.get("Segments"),
                    "InboundSegments": ib.get("Segments"),
                    "Baggage": {"Outbound": ob.get("BaggageAllowance"), "Inbound": ib.get("BaggageAllowance")},
                    "UpSellBrandList": ob.get("UpSellBrandList") if ob.get("UpSellBrandList") is not None else ib.get("UpSellBrandList"),
                    "SeatsRemaining": min(ob.get("SeatsRemaining", 0), ib.get("SeatsRemaining", 0)),
                    "Extra": bdfare_meta,
                    "ItineraryType": "return"
                }
                flights.append(flight_obj)
        # Process one-way (or multi-city one-way) offers if available in offersGroup
        elif response.get("offersGroup"):
            offers_group = response.get("offersGroup")
            if isinstance(offers_group, dict):
                offers = offers_group.get("ob", [])
            elif isinstance(offers_group, list):
                offers = offers_group
            else:
                offers = []
            for item in offers:
                offer = process_bdfare_offer(item.get("offer", {}))
                flight_obj = {
                    "Source": "bdfare",
                    "TraceId": trace_id,
                    "OfferId": offer.get("OfferId"),
                    "ValidatingCarrier": offer.get("ValidatingCarrier"),
                    "Refundable": offer.get("Refundable"),
                    "FareType": offer.get("FareType"),
                    "Pricing": offer.get("PriceBreakdown"),
                    "FareDetails": offer.get("FareDetails"),
                    "Penalty": offer.get("Penalty"),
                    "OutboundSegments": offer.get("Segments"),
                    "InboundSegments": [],
                    "Baggage": offer.get("BaggageAllowance"),
                    "UpSellBrandList": offer.get("UpSellBrandList"),
                    "SeatsRemaining": offer.get("SeatsRemaining"),
                    "Extra": bdfare_meta,
                    "ItineraryType": "oneway"
                }
                flights.append(flight_obj)
        else:
            logger.info("bdfare data received does not contain recognized offersGroup or specialReturnOffersGroup.")

    # --- Process flyhub data ---
    if "flyhub" in data:
        flyhub_data = data["flyhub"]
        search_id = flyhub_data.get("SearchId")
        results = flyhub_data.get("Results", [])
        for res in results:
            flight_obj = process_flyhub_result(res)
            # Add flyhub IDs:
            flight_obj["SearchId"] = search_id
            flight_obj["ResultID"] = res.get("ResultID")
            flight_obj["Source"] = "flyhub"
            flights.append(flight_obj)

    return {"Flights": flights}


# updated