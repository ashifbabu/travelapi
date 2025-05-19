from pydantic import BaseModel, Field
from typing import List, Optional

# --- Request Model ---
class AirRulesRequest(BaseModel):
    traceId: str = Field(..., example="80969b97-38a7-4f05-8253-b3cd4598aa5d", description="The trace ID from a previous search or booking.")
    offerId: str = Field(..., example="offer_1_abc", description="The offer ID for which fare rules are requested.") # Changed from offerIds: List[str]

# --- Response Models (mirroring TypedDicts from airrules_bdfare adapter) ---
class RuleDetailModel(BaseModel):
    """Represents a single rule category and its textual information."""
    category_name: str = Field(..., example="Penalties")
    rules_text: str = Field(..., example="CHANGES PER TICKET CHARGE BDT 1200 FOR REISSUE...")

class PaxFareRulesModel(BaseModel):
    """Represents fare rules for a specific passenger type and fare basis code on a route."""
    pax_type: str = Field(..., example="Adult")
    fare_basis_code: str = Field(..., example="EDOMO")
    rule_details: List[RuleDetailModel]

class RouteFareRulesModel(BaseModel):
    """Represents fare rules for a specific route, containing rules for various passenger types."""
    route: str = Field(..., example="DAC→JSR")
    pax_specific_rules: List[PaxFareRulesModel]

# The overall response from the endpoint will be a list of RouteFareRulesModel
# No need for a separate AirRulesResponse model if it's just List[RouteFareRulesModel]
# However, if you want to wrap it with metadata, you could define:
# class AirRulesResponse(BaseModel):
#     traceId: str
#     rules_by_route: List[RouteFareRulesModel]
# For now, we'll assume the endpoint directly returns List[RouteFareRulesModel]