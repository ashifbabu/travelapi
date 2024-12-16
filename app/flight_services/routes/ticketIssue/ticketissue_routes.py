from fastapi import APIRouter, HTTPException, Body
from app.flight_services.models.ticketIssue.ticketissue_request import UnifiedTicketIssueRequest
from app.flight_services.services.ticketissue_service import process_ticket_issue
import logging

# Initialize router and logger
router = APIRouter()
logger = logging.getLogger("ticketissue_routes")

@router.post("/issue", tags=["TicketIssue"])
async def issue_ticket(payload: UnifiedTicketIssueRequest = Body(...)):
    """
    Endpoint to process Ticket Issue requests.
    """
    try:
        logger.info("Received Ticket Issue request.")
        logger.debug(f"Request payload: {payload.dict()}")

        # Process the ticket issue request
        response = await process_ticket_issue(payload)

        # Log and return the response
        logger.info("Ticket Issue processed successfully.")
        return response

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Unexpected error during Ticket Issue processing.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
