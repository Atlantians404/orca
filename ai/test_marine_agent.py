from ai.agents.marine_agent.marine_agent import run_marine_agent
from ai.schemas.location import Location
from ai.schemas.time import TimeContext


state = {
    "prompt": "Find the nearest PFZ",
    "conversation_summary": None,

    "location": Location(
        latitude=13.08,
        longitude=80.27
    ),

    "time_context": TimeContext(
        date="2026-08-30",
        start_time="08:00"
    ),

    "selected_agents": ["marine"],
    "selected_engines": [],

    "agent_data": {},

    "pfz_candidates": [],

    "risk_result": None,
    "route_result": None,

    "response": None
}


result = run_marine_agent(state)


print("\nSTATE:")
print("pfz_candidates")


print("\nNUMBER OF PFZ CANDIDATES:")
print(len(result["pfz_candidates"]))


print("\nTOP PFZ CANDIDATES:")

for pfz in result["pfz_candidates"]:
    print(
        pfz["id"],
        "|",
        pfz["coastal_reference"],
        "|",
        pfz["latitude"],
        pfz["longitude"],
        "|",
        pfz["distance_from_source_km"],
        "km"
    )