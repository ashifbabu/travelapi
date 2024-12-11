import logging

# Set up logger
logger = logging.getLogger("airprebook_bdfare")
logger.setLevel(logging.INFO)  # Change to DEBUG for more verbose logs
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
def adapt_to_bdfare_airprebook_request(unified_request: dict) -> dict:
    """
    Adapt a unified air prebook request into a BDFare-compatible request.
    """
    # Validate that all required keys exist
    if "traceId" not in unified_request:
        raise KeyError("Missing 'traceId' in request.")
    if "offerId" not in unified_request:
        raise KeyError("Missing 'offerId' in request.")
    if "request" not in unified_request:
        raise KeyError("Missing 'request' in request.")
    
    request_data = unified_request["request"]

    if "contactInfo" not in request_data:
        raise KeyError("Missing 'contactInfo' in request.")
    if "paxList" not in request_data:
        raise KeyError("Missing 'paxList' in request.")
    
    contact_info = request_data["contactInfo"]
    if "phone" not in contact_info:
        raise KeyError("Missing 'phone' in 'contactInfo'.")
    if "emailAddress" not in contact_info:
        raise KeyError("Missing 'emailAddress' in 'contactInfo'.")

    phone_info = contact_info["phone"]
    if "phoneNumber" not in phone_info or "countryDialingCode" not in phone_info:
        raise KeyError("Missing 'phoneNumber' or 'countryDialingCode' in 'phone'.")

    # Construct the BDFare-compatible payload
    payload = {
        "traceId": unified_request["traceId"],
        "offerId": unified_request["offerId"],
        "request": {
            "contactInfo": {
                "phone": {
                    "phoneNumber": phone_info["phoneNumber"],
                    "countryDialingCode": phone_info["countryDialingCode"]
                },
                "emailAddress": contact_info["emailAddress"]
            },
            "paxList": []
        }
    }

    # Pax details
    for pax in request_data["paxList"]:
        if "ptc" not in pax:
            raise KeyError("Missing 'ptc' in 'paxList' item.")
        if "individual" not in pax:
            raise KeyError("Missing 'individual' in 'paxList' item.")

        individual = pax["individual"]
        required_individual_fields = ["givenName", "surname", "gender", "birthdate", "nationality", "identityDoc"]
        for field in required_individual_fields:
            if field not in individual:
                raise KeyError(f"Missing '{field}' in 'individual' for pax.")

        pax_entry = {
            "ptc": pax["ptc"],
            "individual": {
                "givenName": individual["givenName"],
                "surname": individual["surname"],
                "gender": individual["gender"],
                "birthdate": individual["birthdate"],
                "nationality": individual["nationality"],
                "identityDoc": individual["identityDoc"]
            }
        }
        payload["request"]["paxList"].append(pax_entry)

    return payload
