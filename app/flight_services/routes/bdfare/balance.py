from fastapi import APIRouter, HTTPException
from app.flight_services.clients.bdfare_client import BDFAREClient
import logging

router = APIRouter()

@router.get("/balance", tags=["Flights"])
async def get_bdfare_balance():
    """
    Endpoint to retrieve the current balance from BDFARE.
    """
    try:
        client = BDFAREClient()
        balance = client.get_balance()
        return balance
    except HTTPException as e:
        # Log and raise HTTP errors
        logging.error(f"Error while fetching balance: {e.detail}")
        raise e
    except Exception as e:
        # Catch and log unexpected errors
        logging.error(f"Unexpected error in /balance endpoint: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
