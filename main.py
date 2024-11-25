from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access environment variables (for example)
APP_TITLE = os.getenv("APP_TITLE", "Travel API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "API for flight and travel related services")

# Import routers
from app.flight_services.routes.flyhub.auth import router as flyhub_auth_endpoint
from app.flight_services.routes.flyhub import balance as flyhub_balance_routes
from app.flight_services.routes.bdfare import balance as bdfare_balance_routes
from app.hotel_services.routes import hotel_router
from app.bus_services.routes import bus_router
from app.car_services.routes import car_router
from app.event_services.routes import event_router
from app.holidays_services.routes import holiday_router
from app.insurance_services.routes import insurance_router
from app.train_services.routes import train_router
from app.flight_services.routes.flyhub.search import router as flyhub_search_router
from app.flight_services.routes.bdfare import search as bdfare_search_router
from app.flight_services.routes.bdfare import offerPrice as bdfare_offerPrice_router
from app.flight_services.routes.bdfare import miniRule as bdfare_miniRule_router
from app.flight_services.routes.bdfare import fareRules as bdfare_fareRules_router
from app.flight_services.routes.bdfare import airPreBook as bdfare_airPreBook_router
from app.flight_services.routes.combined import combined_search
#test this is a test line added
# Initialize FastAPI app
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    openapi_url="/openapi.json",
    description=APP_DESCRIPTION
)

# Include service routers with appropriate prefixes and tags
app.include_router(flyhub_auth_endpoint, prefix="/api/flyhub", tags=["Flights"])
app.include_router(flyhub_balance_routes.router, prefix="/api/flyhub", tags=["Flights"])
app.include_router(bdfare_balance_routes.router, prefix="/api/bdfare", tags=["Flights"])
app.include_router(hotel_router, prefix="/hotels", tags=["Hotels"])
app.include_router(bus_router, prefix="/bus", tags=["Bus"])
app.include_router(car_router, prefix="/cars", tags=["Cars"])
app.include_router(event_router, prefix="/events", tags=["Events"])
app.include_router(holiday_router, prefix="/holidays", tags=["Holidays"])
app.include_router(insurance_router, prefix="/insurance", tags=["Insurance"])
app.include_router(train_router, prefix="/trains", tags=["Trains"])
app.include_router(bdfare_search_router.router, prefix="/api/bdfare", tags=["Flights"])
app.include_router(bdfare_offerPrice_router.router, prefix="/api/bdfare", tags=["Flights"])
app.include_router(bdfare_miniRule_router.router, prefix="/api/bdfare", tags=["Flights"])
app.include_router(bdfare_fareRules_router.router, prefix="/api/bdfare", tags=["Flights"])
app.include_router(bdfare_airPreBook_router.router, prefix="/api/bdfare", tags=["Flights"])
app.include_router(combined_search.router, prefix="/api/combined", tags=["Flights"])
app.include_router(flyhub_search_router, prefix="/api/flyhub", tags=["Flights"])


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Travel API!"}


@app.head("/")
async def read_root_head():
    return {"message": "Welcome to the Travel API!"}