from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class IdentityDoc(BaseModel):
    identityDocType: str
    identityDocID: str
    expiryDate: str

class Individual(BaseModel):
    givenName: str
    surname: str
    gender: str
    birthdate: str
    nationality: str
    identityDoc: IdentityDoc

class PaxList(BaseModel):
    ptc: str
    individual: Individual

class Phone(BaseModel):
    phoneNumber: str
    countryDialingCode: str

class ContactInfo(BaseModel):
    phone: Phone
    emailAddress: EmailStr

class AirPrebookRequestData(BaseModel):
    contactInfo: ContactInfo
    paxList: List[PaxList]

class UnifiedAirPrebookRequest(BaseModel):
    source: str = Field(..., description="Data source, e.g., 'bdfare' or 'flyhub'")
    traceId: str
    offerId: List[str]
    request: AirPrebookRequestData
