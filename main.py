from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import pandas as pd
import json
import logging
from fastapi import Query
from typing import List
from pydantic import BaseModel, Field, validator
from typing import Optional
from starlette.middleware.cors import CORSMiddleware
from app.flight_services.routes.combined import combined_search
from app.flight_services.routes.rules import router as rules_router
from app.flight_services.routes.airprice.airprice_routes import router as airprice_router
from app.flight_services.routes.airprebook.airprebook_routes import router as airprebook_router
from app.flight_services.routes.airbook.airbook_routes import router as airbook_router
from app.flight_services.routes.airretrieve.airretrieve_routes import router as airretrieve_router
from app.flight_services.services.ailineLogoService import get_airline_by_id
# Initialize FastAPI app
app = FastAPI(
    title="Travel Services API",
    description="API for flight services, rules, air pricing, prebooking, and booking",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure logging
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Define the Pydantic model
class Airport(BaseModel):
    city: Optional[str]
    country: Optional[str]  # Should contain the actual country
    airportName: Optional[str]  # Should contain the name of the airport
    code: Optional[str] = None  # Handle IATA code being optional

    @validator('code', pre=True, always=True)
    def set_code_to_empty_string_if_none(cls, v):
        return v or "N/A"  # Replace null IATA codes with "N/A"

    class Config:
        schema_extra = {
            "example": {
                "city": "Dubai",
                "country": "United Arab Emirates",
                "airportName": "Dubai International Airport",
                "code": "DXB"  # Example, adjust according to actual data
            }
        }

# Global variable to hold the data
airports_df = None

# Load the CSV file into a DataFrame
@app.on_event("startup")
async def load_airport_data():
    global airports_df
    with open('app/flight_services/data/airports.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    airports_df = pd.json_normalize(data)  # Convert JSON to DataFrame
    airports_df.rename(columns={
        'IATA': 'iata_code', 
        'Country': 'country', 
        'Airport name': 'airport_name', 
        'City': 'city'
    }, inplace=True)
    airports_df.dropna(subset=['iata_code'], inplace=True)  # Ensure no null IATA codes
    logger.info("Airport data loaded successfully.")


# Endpoint to get airport data
@app.get("/api/airports/", response_model=List[Airport])
async def search_airports(query: Optional[str] = Query(None, description="Search by airport code or name")):
    if not query:
        return []
    query = query.lower().strip()
    results = airports_df[
        (airports_df['iata_code'].str.lower() == query) |
        (airports_df['airport_name'].str.lower().str.contains(query)) |
        (airports_df['city'].str.lower().str.contains(query))
    ]
    return [Airport(
        city=row['city'],
        country=row['country'],
        airportName=row['airport_name'],
        code=row['iata_code']
    ) for index, row in results.iterrows()]


@app.get("/airline/{airline_id}/logo", response_model=str, status_code=200)
def read_airline_logo(airline_id: str):
    airline = get_airline_by_id(airline_id)
    if airline is None:
        raise HTTPException(status_code=404, detail="Airline not found")
    return airline.get('logo', 'Logo not available')


# Register other routes
app.include_router(combined_search.router, prefix="/api/combined", tags=["Flights"])
app.include_router(rules_router, prefix="/api/rules", tags=["Rules"])
app.include_router(airprice_router, prefix="/api/airprice", tags=["AirPrice"])
app.include_router(airprebook_router, prefix="/api/airprebook", tags=["AirPreBook"])
app.include_router(airbook_router, prefix="/api/airbook", tags=["AirBook"])
app.include_router(airretrieve_router, prefix="/api/airretrieve", tags=["AirRetrieve"])

@app.get("/", tags=["Health"])
async def health_check():
    logger.info("Health check endpoint accessed.")
    return {"status": "ok", "message": "Service is running"}

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error("Validation error occurred: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Request validation failed. Check your input format."
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unexpected error occurred: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        },
    )


# from fastapi import FastAPI
# from dotenv import load_dotenv
# import os

# # Load .env file
# load_dotenv()

# # Access environment variables (for example)
# APP_TITLE = os.getenv("APP_TITLE", "Travel API")
# APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
# APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "API for flight and travel related services")

# # Import routers
# from app.flight_services.routes.flyhub.auth import router as flyhub_auth_endpoint
# from app.flight_services.routes.flyhub import balance as flyhub_balance_routes
# from app.flight_services.routes.bdfare import balance as bdfare_balance_routes
# from app.hotel_services.routes import hotel_router
# from app.bus_services.routes import bus_router
# from app.car_services.routes import car_router
# from app.event_services.routes import event_router
# from app.holidays_services.routes import holiday_router
# from app.insurance_services.routes import insurance_router
# from app.train_services.routes import train_router
# from app.flight_services.routes.flyhub.search import router as flyhub_search_router
# from app.flight_services.routes.bdfare import search as bdfare_search_router
# from app.flight_services.routes.bdfare import offerPrice as bdfare_offerPrice_router
# from app.flight_services.routes.bdfare import miniRule as bdfare_miniRule_router
# from app.flight_services.routes.bdfare import fareRules as bdfare_fareRules_router
# from app.flight_services.routes.bdfare import airPreBook as bdfare_airPreBook_router
# from app.flight_services.routes.bdfare import airbook as bdfare_airbook_router
# from app.flight_services.routes.bdfare import bookingRetrieve as bdfare_bookingRetrieve_router
# from app.flight_services.routes.bdfare import orderReshopPrice as bdfare_orderReshopPrice_router
# from app.flight_services.routes.bdfare import orderChange as bdfare_orderChange_router
# from app.flight_services.routes.bdfare import orderCancel as bdfare_orderCancel_router
# from app.flight_services.routes.combined import combined_search
# #test this is a test line added
# # Initialize FastAPI app
# app = FastAPI(
#     title=APP_TITLE,
#     version=APP_VERSION,
#     openapi_url="/openapi.json",
#     description=APP_DESCRIPTION
# )

# # Include service routers with appropriate prefixes and tags
# app.include_router(flyhub_auth_endpoint, prefix="/api/flyhub", tags=["Flights"])
# app.include_router(flyhub_balance_routes.router, prefix="/api/flyhub", tags=["Flights"])
# app.include_router(bdfare_balance_routes.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(hotel_router, prefix="/hotels", tags=["Hotels"])
# app.include_router(bus_router, prefix="/bus", tags=["Bus"])
# app.include_router(car_router, prefix="/cars", tags=["Cars"])
# app.include_router(event_router, prefix="/events", tags=["Events"])
# app.include_router(holiday_router, prefix="/holidays", tags=["Holidays"])
# app.include_router(insurance_router, prefix="/insurance", tags=["Insurance"])
# app.include_router(train_router, prefix="/trains", tags=["Trains"])
# app.include_router(bdfare_search_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_offerPrice_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_miniRule_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_fareRules_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_airPreBook_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_airbook_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_bookingRetrieve_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_orderReshopPrice_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_orderChange_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(bdfare_orderCancel_router.router, prefix="/api/bdfare", tags=["Flights"])
# app.include_router(combined_search.router, prefix="/api/combined", tags=["Flights"])
# app.include_router(flyhub_search_router, prefix="/api/flyhub", tags=["Flights"])


# # Root endpoint
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Travel API!"}


# @app.head("/")
# async def read_root_head():
#     return {"message": "Welcome to the Travel API!"}