from app.flight_services.models.ticketIssue.ticketissue_request import UnifiedTicketIssueRequest, FlyHubTicketIssueRequest


def adapt_to_flyhub_ticket_issue_request(payload: UnifiedTicketIssueRequest) -> FlyHubTicketIssueRequest:
    """
    Adapt a UnifiedTicketIssueRequest to a FlyHub-specific Ticket Issue request.

    Args:
        payload (UnifiedTicketIssueRequest): Unified ticket issue request payload.

    Returns:
        FlyHubTicketIssueRequest: Transformed request specific to FlyHub.
    """
    return FlyHubTicketIssueRequest(
        BookingID=payload.bookingId,
        IsAcceptedPriceChangeandIssueTicket=payload.acceptPriceChange
    )
