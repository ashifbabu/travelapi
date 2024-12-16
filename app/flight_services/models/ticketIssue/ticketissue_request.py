from pydantic import BaseModel, Field


class UnifiedTicketIssueRequest(BaseModel):
    """
    Unified request model for Ticket Issue.
    """
    bookingId: str = Field(..., description="Unique booking reference or order reference ID.")
    source: str = Field(..., description="Source of the booking (e.g., FlyHub, BDFare).")
    partialPayment: bool = Field(False, description="Indicates if partial payment is allowed (for BDFare).")
    acceptPriceChange: bool = Field(False, description="Indicates if price changes are accepted (for FlyHub).")


class BDFareTicketIssueRequest(BaseModel):
    """
    BDFare-specific request model for Ticket Issue.
    """
    orderReference: str = Field(..., description="Unique order reference for BDFare.")
    issueTicketViaPartialPayment: bool = Field(False, description="Allow ticket issuance via partial payment.")


class FlyHubTicketIssueRequest(BaseModel):
    """
    FlyHub-specific request model for Ticket Issue.
    """
    BookingID: str = Field(..., description="Unique booking ID for FlyHub.")
    IsAcceptedPriceChangeandIssueTicket: bool = Field(False, description="Accept price change and issue the ticket.")
