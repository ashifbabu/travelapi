from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# Enums for fixed value fields
class CabinCodeEnum(str, Enum):
    economy = "Economy"
    business = "Business"
    first = "First"


class TripTypeEnum(str, Enum):
    oneway = "Oneway"
    return_ = "Return"
    multicity = "Multicity"


# Nested models for request structure
class OriginDepRequest(BaseModel):
    iatA_LocationCode: str = Field(..., example="DAC")
    date: str = Field(..., example="2024-12-15")


class DestArrivalRequest(BaseModel):
    iatA_LocationCode: str = Field(..., example="JSR")


class OriginDest(BaseModel):
    originDepRequest: OriginDepRequest
    destArrivalRequest: DestArrivalRequest


class Pax(BaseModel):
    paxID: str = Field(..., example="PAX1")
    ptc: str = Field(..., example="ADT")


class TravelPreferences(BaseModel):
    vendorPref: List[str] = Field(default_factory=list, example=["BG", "AA"])
    cabinCode: CabinCodeEnum = Field(..., example="Economy")


class ShoppingCriteria(BaseModel):
    tripType: TripTypeEnum = Field(..., example="Multicity")
    travelPreferences: TravelPreferences
    returnUPSellInfo: bool = Field(..., example=True)


# Main request model
class FlightSearchRequest(BaseModel):
    pointOfSale: str = Field(..., example="BD")
    source: str = Field(..., example="all", description="Specify data source: 'bdfare', 'flyhub', or 'all'")
    request: dict = Field(..., description="Structured request details including originDest, pax, and shopping criteria.")
    
    # Optional: Define `request` as a nested model for better validation
    # request: FlightRequestDetails


# Model for `request` field details
class FlightRequestDetails(BaseModel):
    originDest: List[OriginDest]
    pax: List[Pax]
    shoppingCriteria: ShoppingCriteria


# Response models remain unchanged
class PriceDetails(BaseModel):
    baseFare: float = Field(..., example=200.0)
    tax: float = Field(..., example=50.0)
    discount: float = Field(..., example=10.0)
    total: float = Field(..., example=240.0)
    currency: str = Field(..., example="USD")


class FlightSegment(BaseModel):
    from_: str = Field(..., alias="from", example="DAC")
    fromAirportName: Optional[str] = Field(None, example="Dhaka Airport")
    to: str = Field(..., example="JSR")
    toAirportName: Optional[str] = Field(None, example="Jessore Airport")
    departureTime: str = Field(..., example="2024-12-15T08:30:00")
    arrivalTime: str = Field(..., example="2024-12-15T10:00:00")
    airlineCode: str = Field(..., example="BG")
    airlineName: Optional[str] = Field(None, example="Biman Bangladesh Airlines")
    flightNumber: str = Field(..., example="BG401")
    cabinClass: str = Field(..., example="Economy")
    durationMinutes: int = Field(..., example=90)


class BaggageDetails(BaseModel):
    from_: str = Field(..., alias="from", example="JFK")
    to: str = Field(..., example="LAX")
    checkIn: Optional[List[dict]] = Field(None, example=[{"paxType": "ADT", "allowance": "20kg"}])
    cabin: Optional[List[dict]] = Field(None, example=[{"paxType": "ADT", "allowance": "7kg"}])


class FlightSearchResponse(BaseModel):
    id: str = Field(..., example="12345")
    airline: str = Field(..., example="AA")
    airlineName: Optional[str] = Field(None, example="American Airlines")
    refundable: bool = Field(..., example=True)
    fareType: str = Field(..., example="OnHold")
    price: PriceDetails
    segments: List[FlightSegment]
    baggageAllowance: List[BaggageDetails]
    seatsRemaining: int = Field(..., example=9)

