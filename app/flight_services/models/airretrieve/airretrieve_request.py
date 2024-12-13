from pydantic import BaseModel, Field
from typing import Optional, Dict


class UnifiedAirRetrieveRequest(BaseModel):
    """
    Model for incoming AirRetrieve request.
    """
    bookingId: str = Field(..., description="Booking reference or order reference ID.")
    source: str = Field(..., description="Source of the booking (e.g., FlyHub, BDFare).")


class FlyHubRetrieveRequest(BaseModel):
    """
    Model for FlyHub-specific AirRetrieve request.
    """
    BookingID: str = Field(..., description="Unique booking ID for FlyHub.")


class BDFareRetrieveRequest(BaseModel):
    """
    Model for BDFare-specific AirRetrieve request.
    """
    orderReference: str = Field(..., description="Unique order reference for BDFare.")


class UnifiedAirRetrieveResponse(BaseModel):
    """
    Unified response model for AirRetrieve.
    """
    bookingId: str = Field(..., description="Unique booking reference.")
    status: str = Field(..., description="Status of the booking (e.g., Confirmed, Canceled).")
    details: Optional[Dict] = Field(None, description="Additional details about the booking.")
