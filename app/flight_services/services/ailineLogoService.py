import json
from typing import Optional

# Load airlines data from a JSON file
def load_airlines_data():
    with open('app/flight_services/data/airlines.json', 'r') as file:
        return json.load(file)

airlines_data = load_airlines_data()

# Function to get airline by ID
def get_airline_by_id(airline_id: str) -> Optional[dict]:
    for airline in airlines_data:
        if airline['id'] == airline_id:
            return airline
    return None
