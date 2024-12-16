from app.flight_services.models.ticketcancel.ticketcancel_request import (
    UnifiedTicketCancelRequest,
    BDFareTicketCancelRequest,
    FlyHubTicketCancelRequest,
)


def adapt_to_bdfare_ticket_cancel_request(payload: UnifiedTicketCancelRequest) -> BDFareTicketCancelRequest:
    """
    Adapt a UnifiedTicketCancelRequest to a BDFare-specific Ticket Cancel request.

    Args:
        payload (UnifiedTicketCancelRequest): Unified ticket cancel request payload.

    Returns:
        BDFareTicketCancelRequest: Transformed request specific to BDFare.
    """
    return BDFareTicketCancelRequest(
        orderReference=payload.bookingId
    )


def adapt_to_flyhub_ticket_cancel_request(payload: UnifiedTicketCancelRequest) -> FlyHubTicketCancelRequest:
    """
    Adapt a UnifiedTicketCancelRequest to a FlyHub-specific Ticket Cancel request.

    Args:
        payload (UnifiedTicketCancelRequest): Unified ticket cancel request payload.

    Returns:
        FlyHubTicketCancelRequest: Transformed request specific to FlyHub.
    """
    return FlyHubTicketCancelRequest(
        BookingID=payload.bookingId
    )
