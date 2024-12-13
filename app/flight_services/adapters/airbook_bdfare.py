from typing import Dict

def adapt_to_bdfare_airbook_request(payload: Dict) -> Dict:
    """
    Adapt a UnifiedAirBookRequest payload to the BDFare-specific format.

    Args:
        payload (Dict): The unified payload as a dictionary.

    Returns:
        Dict: Transformed payload for the BDFare API.
    """
    try:
        # Extract traceId and offerId
        trace_id = payload.get("traceId")
        offer_ids = payload.get("offerId", [])

        # Extract contact info
        contact_info = payload["request"]["contactInfo"]
        contact_phone = contact_info["phone"]
        email_address = contact_info["emailAddress"]

        # Extract passenger list
        pax_list = payload["request"]["paxList"]
        transformed_pax_list = []
        for pax in pax_list:
            individual = pax["individual"]
            identity_doc = individual.get("identityDoc", {})
            transformed_pax = {
                "ptc": pax["ptc"],
                "individual": {
                    "givenName": individual["givenName"],
                    "surname": individual["surname"],
                    "gender": individual["gender"],
                    "birthdate": individual["birthdate"],
                    "nationality": individual.get("nationality", ""),
                    "identityDoc": {
                        "identityDocType": identity_doc.get("identityDocType", ""),
                        "identityDocID": identity_doc.get("identityDocID", ""),
                        "expiryDate": identity_doc.get("expiryDate", ""),
                    },
                },
            }
            transformed_pax_list.append(transformed_pax)

        # Construct the BDFare-compatible request payload
        bdfare_request = {
            "traceId": trace_id,
            "offerId": offer_ids,
            "request": {
                "contactInfo": {
                    "phone": {
                        "phoneNumber": contact_phone["phoneNumber"],
                        "countryDialingCode": contact_phone["countryDialingCode"],
                    },
                    "emailAddress": email_address,
                },
                "paxList": transformed_pax_list,
            },
        }

        return bdfare_request

    except KeyError as e:
        raise ValueError(f"Missing required key in payload: {e}")
