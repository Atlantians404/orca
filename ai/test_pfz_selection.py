from ai.agents.marine_agent.marine_agent import run_marine_agent
from ai.schemas.location import Location
from ai.schemas.time import TimeContext, TimeSlot


state = {
    "location": Location(
        latitude=13.08,
        longitude=80.27
    ),

    "time_context": TimeContext(
        slots=[
            TimeSlot(
                date="2026-08-30",
                start_time="08:00"
            )
        ]
    ),

    "selected_pfz_id": "PFZ11"
}


result = run_marine_agent(state)


print("\nSTATE:")
print("pfz_candidates:", len(result["pfz_candidates"]))

print("\nSELECTED PFZ:")

selected = result["selected_pfz"]

if selected:
    print("ID:", selected["id"])
    print("Coastal Reference:", selected["coastal_reference"])
    print("Latitude:", selected["latitude"])
    print("Longitude:", selected["longitude"])
    print("Distance:", selected["distance_from_source_km"], "km")
    print("Direction:", selected["direction"])
    print("Depth:", selected["depth_m"])
else:
    print("No PFZ selected")