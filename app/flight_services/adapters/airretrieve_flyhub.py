from app.flight_services.models.airretrieve.airretrieve_request import (
    UnifiedAirRetrieveRequest,
    FlyHubRetrieveRequest,
    BDFareRetrieveRequest,
)


def convert_flyhub_to_bdfare_airretrieve_request(payload: FlyHubRetrieveRequest) -> BDFareRetrieveRequest:
    """
    Convert a FlyHub-specific AirRetrieve request to a BDFare-specific AirRetrieve request.

    Args:
        payload (FlyHubRetrieveRequest): The FlyHub AirRetrieve request.

    Returns:
        BDFareRetrieveRequest: Transformed request specific to BDFare.
    """
    return BDFareRetrieveRequest(
        orderReference=payload.BookingID  # Map FlyHub's `BookingID` to BDFare's `orderReference`
    )
