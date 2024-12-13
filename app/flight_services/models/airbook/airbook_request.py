from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class IdentityDoc(BaseModel):
    identityDocType: str = Field(..., description="Type of identity document (e.g., Passport).")
    identityDocID: str = Field(..., description="Identity document number.")
    expiryDate: str = Field(..., description="Expiry date of the document in YYYY-MM-DD format.")

class Individual(BaseModel):
    givenName: str = Field(..., description="Given name of the individual.")
    surname: str = Field(..., description="Surname of the individual.")
    gender: str = Field(..., description="Gender of the individual (Male/Female).")
    birthdate: str = Field(..., description="Birth date of the individual in YYYY-MM-DD format.")
    nationality: str = Field(..., description="Nationality of the individual.")
    identityDoc: IdentityDoc = Field(..., description="Identity document details.")

class Pax(BaseModel):
    ptc: str = Field(..., description="Passenger type code (e.g., Adult, Child, Infant).")
    individual: Individual = Field(..., description="Details of the individual passenger.")

class Phone(BaseModel):
    phoneNumber: str = Field(..., description="Phone number without country code.")
    countryDialingCode: str = Field(..., description="Country dialing code.")

class ContactInfo(BaseModel):
    phone: Phone = Field(..., description="Phone contact details.")
    emailAddress: EmailStr = Field(..., description="Email address of the contact.")

class Request(BaseModel):
    contactInfo: ContactInfo = Field(..., description="Contact information for the booking.")
    paxList: List[Pax] = Field(..., description="List of passengers for the booking.")

class UnifiedAirBookRequest(BaseModel):
    traceId: str = Field(..., description="Unique trace ID for the booking.")
    offerId: List[str] = Field(..., description="List of offer IDs related to the booking.")
    request: Request = Field(..., description="Request details including contact info and passengers.")
    source: str = Field(..., description="Source of the request (e.g., BDFare, FlyHub).")
