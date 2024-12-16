from fastapi import HTTPException
from app.flight_services.models.ticketcancel.ticketcancel_request import UnifiedTicketCancelRequest
from app.flight_services.clients.bdfare_client import fetch_bdfare_ticket_cancel
from app.flight_services.clients.flyhub_client import fetch_flyhub_ticket_cancel
from app.flight_services.adapters.ticketcancel_adapters import (
    adapt_to_bdfare_ticket_cancel_request,
    adapt_to_flyhub_ticket_cancel_request,
)
import logging

logger = logging.getLogger("ticketcancel_service")


async def process_ticket_cancel(payload: UnifiedTicketCancelRequest) -> dict:
    """
    Process the Ticket Cancel request based on the source.

    Args:
        payload (UnifiedTicketCancelRequest): Unified request payload.

    Returns:
        dict: Raw response from the respective API.

    Raises:
        HTTPException: If the source is unsupported or an error occurs.
    """
    source = payload.source.lower()

    if source == "bdfare":
        logger.info("Processing BDFare Ticket Cancel request.")
        
        # Convert Unified Request to BDFare-specific Request
        bdfare_request = adapt_to_bdfare_ticket_cancel_request(payload)
        logger.debug(f"BDFare request: {bdfare_request.dict()}")
        
        # Fetch data from BDFare
        bdfare_response = await fetch_bdfare_ticket_cancel(bdfare_request.dict())
        logger.debug(f"BDFare response: {bdfare_response}")
        return bdfare_response

    elif source == "flyhub":
        logger.info("Processing FlyHub Ticket Cancel request.")
        
        # Convert Unified Request to FlyHub-specific Request
        flyhub_request = adapt_to_flyhub_ticket_cancel_request(payload)
        logger.debug(f"FlyHub request: {flyhub_request.dict()}")
        
        # Fetch data from FlyHub
        flyhub_response = await fetch_flyhub_ticket_cancel(flyhub_request.dict())
        logger.debug(f"FlyHub response: {flyhub_response}")
        return flyhub_response

    else:
        logger.error(f"Unsupported source: {source}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source: {source}",
        )
