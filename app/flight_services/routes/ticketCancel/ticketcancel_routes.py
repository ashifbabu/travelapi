from fastapi import APIRouter, HTTPException, Body
from app.flight_services.models.ticketcancel.ticketcancel_request import UnifiedTicketCancelRequest
from app.flight_services.services.ticketcancel_service import process_ticket_cancel
import logging

router = APIRouter()
logger = logging.getLogger("ticketcancel_routes")

@router.post("/cancel", tags=["TicketCancel"])
async def cancel_ticket(payload: UnifiedTicketCancelRequest = Body(...)):
    """
    Endpoint to process Ticket Cancel requests.
    """
    try:
        logger.info("Received Ticket Cancel request.")
        logger.debug(f"Request payload: {payload.dict()}")

        # Process the ticket cancel request
        response = await process_ticket_cancel(payload)

        logger.info("Ticket Cancel processed successfully.")
        return response

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Unexpected error during Ticket Cancel processing.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
