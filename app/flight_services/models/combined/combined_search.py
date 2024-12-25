#app\flight_services\models\combined\combined_search.py
from pydantic import BaseModel, Field
from typing import List, Optional


class PriceDetails(BaseModel):
    baseFare: float = Field(..., example=200.0)
    tax: float = Field(..., example=50.0)
    discount: float = Field(..., example=10.0)
    total: float = Field(..., example=240.0)
    currency: str = Field(..., example="USD")


class FlightSegment(BaseModel):
    from_: str = Field(..., alias="from")
    fromAirportName: Optional[str]
    to: str
    toAirportName: Optional[str]
    departureTime: str
    arrivalTime: str
    airlineCode: str
    airlineName: Optional[str]
    flightNumber: str
    cabinClass: str
    durationMinutes: str

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


class FlightSearchRequest(BaseModel):
    pointOfSale: str = Field(..., example="BD")
    source: str = Field(..., example="all", description="Specify data source: 'bdfare', 'flyhub', or 'all'")
    request: dict  # This can be further broken into nested models for validation.


