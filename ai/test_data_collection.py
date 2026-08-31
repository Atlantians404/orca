from ai.agents.data_collection_agent.data_collection_agent import (
    run_data_collection_agent
)

from ai.schemas.location import Location
from ai.schemas.time import TimeContext, TimeSlot


state = {
    "prompt": "Find marine conditions near my nearest PFZ",
    
    "location": Location(
        latitude=13.08,
        longitude=80.27
    ),

    "time_context": TimeContext(
        slots=[
            TimeSlot(
                date="2026-08-30",
                start_time="08:00",
                end_time=None
            )
        ]
    ),

    "selected_pfz": {
        "id": "PFZ11",
        "coastal_reference": "Chinna Neelankarai",
        "latitude": 12.916389,
        "longitude": 80.455833,
        "distance_from_source_km": 27.14,
        "direction": "SE",
        "depth_m": {
            "min": 64,
            "max": 69
        }
    },

    "agent_data": {}
}


result = run_data_collection_agent(state)


print("\nDATA COLLECTION RESULT")
print("======================")

print("\nPFZ:")
print(result["agent_data"]["pfz"]["id"])

print("\nLocation:")
print(result["agent_data"]["collection_location"])

print("\nTime:")
print(result["agent_data"]["collection_time"])

print("\nWeather:")
print(result["agent_data"]["weather"])

print("\nMarine:")
print(result["agent_data"]["marine"])