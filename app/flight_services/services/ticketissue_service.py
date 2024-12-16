from fastapi import HTTPException
from app.flight_services.models.ticketIssue.ticketissue_request import (
    UnifiedTicketIssueRequest,
    BDFareTicketIssueRequest,
    FlyHubTicketIssueRequest,
)
from app.flight_services.clients.bdfare_client import fetch_bdfare_ticket_issue
from app.flight_services.clients.flyhub_client import fetch_flyhub_ticket_issue
import logging
from app.flight_services.adapters.ticketissue_bdfare import adapt_to_bdfare_ticket_issue_request
from app.flight_services.adapters.ticketissue_flyhub import adapt_to_flyhub_ticket_issue_request
# Initialize logger
logger = logging.getLogger("ticketissue_service")


async def process_ticket_issue(payload: UnifiedTicketIssueRequest) -> dict:
    source = payload.source.lower()

    if source == "bdfare":
        logger.info("Processing BDFare Ticket Issue request.")
        
        # Convert Unified Request to BDFare-specific Request
        bdfare_request = adapt_to_bdfare_ticket_issue_request(payload)
        logger.debug(f"BDFare request: {bdfare_request.dict()}")
        
        # Fetch data from BDFare
        return await fetch_bdfare_ticket_issue(bdfare_request.dict())

    elif source == "flyhub":
        logger.info("Processing FlyHub Ticket Issue request.")
        
        # Convert Unified Request to FlyHub-specific Request
        flyhub_request = adapt_to_flyhub_ticket_issue_request(payload)
        logger.debug(f"FlyHub request: {flyhub_request.dict()}")
        
        # Fetch data from FlyHub
        return await fetch_flyhub_ticket_issue(flyhub_request.dict())

    else:
        logger.error(f"Unsupported source: {source}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source: {source}",
        )