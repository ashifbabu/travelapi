from app.flight_services.models.airretrieve.airretrieve_request import UnifiedAirRetrieveRequest, BDFareRetrieveRequest


def adapt_to_bdfare_airretrieve_request(payload: UnifiedAirRetrieveRequest) -> BDFareRetrieveRequest:
    """
    Adapt a UnifiedAirRetrieveRequest to a BDFare-specific AirRetrieve request.

    Args:
        payload (UnifiedAirRetrieveRequest): The unified AirRetrieve request.

    Returns:
        BDFareRetrieveRequest: Transformed request specific to BDFare.
    """
    return BDFareRetrieveRequest(
        orderReference=payload.bookingId  # Map the unified `bookingId` to BDFare's `orderReference`
    )
