from app.flight_services.models.ticketIssue.ticketissue_request import UnifiedTicketIssueRequest, BDFareTicketIssueRequest


def adapt_to_bdfare_ticket_issue_request(payload: UnifiedTicketIssueRequest) -> BDFareTicketIssueRequest:
    """
    Adapt a UnifiedTicketIssueRequest to a BDFare-specific Ticket Issue request.

    Args:
        payload (UnifiedTicketIssueRequest): Unified ticket issue request payload.

    Returns:
        BDFareTicketIssueRequest: Transformed request specific to BDFare.
    """
    return BDFareTicketIssueRequest(
        orderReference=payload.bookingId,
        issueTicketViaPartialPayment=payload.partialPayment
    )
