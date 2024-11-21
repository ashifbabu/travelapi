from pydantic import BaseModel, Field
from typing import Dict, Any

class RequestPayload(BaseModel):
    pointOfSale: str = Field(example="BD")
    request: Dict[str, Any] = Field(
        example={
            "originDest": [
                {
                    "originDepRequest": {
                        "iatA_LocationCode": "JSR",
                        "date": "2024-12-15"
                    },
                    "destArrivalRequest": {
                        "iatA_LocationCode": "DAC"
                    }
                }
            ],
            "pax": [
                {
                    "paxID": "PAX1",
                    "ptc": "ADT"
                }
            ],
            "shoppingCriteria": {
                "tripType": "Oneway",
                "travelPreferences": {
                    "vendorPref": [],
                    "cabinCode": "Economy"
                },
                "returnUPSellInfo": True
            }
        }
    )
