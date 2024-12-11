def convert_bdfare_to_flyhub_airprebook_request(payload: dict) -> dict:
    """
    Convert a BDFare-compatible AirPrebook request payload to FlyHub-compatible payload.

    Args:
        payload (dict): The unified request payload.

    Returns:
        dict: Transformed payload for FlyHub.
    """
    try:
        # Extract traceId and offerId from the payload
        search_id = payload.get("traceId")
        result_id = payload.get("offerId", [])[0]

        # Extract passenger details
        pax_list = payload["request"]["paxList"]
        contact_info = payload["request"]["contactInfo"]
        passengers = []

        for pax in pax_list:
            individual = pax["individual"]

            # Extract loyalty program details only if sellSSR exists and has data
            loyalty_program = pax.get("sellSSR", [{}])[0].get("loyaltyProgramAccount", {})
            ffrequent_airline = loyalty_program.get("airlineDesigCode", "")
            frequent_number = loyalty_program.get("accountNumber", "")

            passenger_data = {
                "Title": "Mr" if individual["gender"].lower() == "male" else "Ms",
                "FirstName": individual["givenName"],
                "LastName": individual["surname"],
                "PaxType": pax["ptc"],
                "DateOfBirth": individual["birthdate"],
                "Gender": individual["gender"],
                "PassportNumber": individual.get("identityDoc", {}).get("identityDocID", ""),
                "PassportExpiryDate": individual.get("identityDoc", {}).get("expiryDate", ""),
                "PassportNationality": individual.get("nationality", ""),
                "Address1": "",
                "Address2": "",
                "CountryCode": "BD",  # Assuming Bangladesh as default; modify if needed
                "Nationality": individual.get("nationality", ""),
                "ContactNumber": f"{contact_info['phone']['countryDialingCode']}{contact_info['phone']['phoneNumber']}",
                "Email": contact_info["emailAddress"],
                "IsLeadPassenger": True if pax_list.index(pax) == 0 else False,
                "FFAirline": ffrequent_airline,
                "FFNumber": frequent_number,
                "Baggage": [{"BaggageID": ""}],  # Placeholder for baggage information
                "Meal": [{"MealID": ""}],  # Placeholder for meal information
            }

            passengers.append(passenger_data)

        # Construct FlyHub-compatible payload
        flyhub_payload = {
            "SearchID": search_id,
            "ResultID": result_id,
            "Passengers": passengers,
            "PromotionCode": "",
        }

        return flyhub_payload

    except KeyError as e:
        raise ValueError(f"Missing required key in payload: {e}")
