from pydantic import BaseModel, Field


class UnifiedTicketCancelRequest(BaseModel):
    """
    Unified request model for Ticket Cancel.
    """
    bookingId: str = Field(..., description="Unique booking reference or order reference ID.")
    source: str = Field(..., description="Source of the booking (e.g., FlyHub, BDFare).")


class BDFareTicketCancelRequest(BaseModel):
    """
    BDFare-specific request model for Ticket Cancel.
    """
    orderReference: str = Field(..., description="Unique order reference for BDFare.")


class FlyHubTicketCancelRequest(BaseModel):
    """
    FlyHub-specific request model for Ticket Cancel.
    """
    BookingID: str = Field(..., description="Unique booking ID for FlyHub.")
