from typing import Dict

def convert_flyhub_to_bdfare_airbook_request(payload: Dict) -> Dict:
    """
    Convert a FlyHub-compatible AirBook request payload to BDFare-compatible payload.

    Args:
        payload (Dict): The FlyHub AirBook request payload.

    Returns:
        Dict: Transformed payload for the BDFare API.
    """
    try:
        # Extract search and result IDs
        trace_id = payload.get("SearchID")
        offer_id = [payload.get("ResultID")]

        # Transform Passengers
        passengers = payload.get("Passengers", [])
        transformed_pax_list = []
        for pax in passengers:
            # Map FlyHub passenger fields to BDFare format
            individual = {
                "givenName": pax.get("FirstName"),
                "surname": pax.get("LastName"),
                "gender": pax.get("Gender"),
                "birthdate": pax.get("DateOfBirth"),
                "nationality": pax.get("Nationality"),
                "identityDoc": {
                    "identityDocType": "Passport",  # Assuming 'Passport' for all
                    "identityDocID": pax.get("PassportNumber", ""),
                    "expiryDate": pax.get("PassportExpiryDate", ""),
                },
            }
            transformed_pax = {
                "ptc": pax.get("PaxType"),
                "individual": individual,
            }
            transformed_pax_list.append(transformed_pax)

        # Construct Contact Info
        lead_passenger = next((p for p in passengers if p.get("IsLeadPassenger")), {})
        contact_info = {
            "phone": {
                "phoneNumber": lead_passenger.get("ContactNumber", "")[-7:],  # Extract last 7 digits
                "countryDialingCode": lead_passenger.get("ContactNumber", "")[:-7],  # Extract dialing code
            },
            "emailAddress": lead_passenger.get("Email", ""),
        }

        # Construct the BDFare-compatible request payload
        bdfare_request = {
            "traceId": trace_id,
            "offerId": offer_id,
            "request": {
                "contactInfo": contact_info,
                "paxList": transformed_pax_list,
            },
        }

        return bdfare_request

    except KeyError as e:
        raise ValueError(f"Missing required key in payload: {e}")
