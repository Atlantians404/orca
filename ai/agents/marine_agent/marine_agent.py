from typing import Any

from ai.tools.marine_tools import get_pfz_candidates


def run_marine_agent(
    state: dict[str, Any]
) -> dict[str, Any]:
    """
    Run the Marine Agent and update AgentState
    with PFZ candidate information.
    """

    location = state.get("location")
    time_context = state.get("time_context")

    if location is None:
        return {
            **state,
            "pfz_candidates": []
        }

    if location.latitude is None or location.longitude is None:
        return {
            **state,
            "pfz_candidates": []
        }

    if time_context is None or time_context.date is None:
        return {
            **state,
            "pfz_candidates": []
        }

    # Build timestamp
    requested_time = time_context.date

    if time_context.start_time:
        requested_time += f"T{time_context.start_time}:00"

    # Get PFZ candidates
    result = get_pfz_candidates(
        latitude=location.latitude,
        longitude=location.longitude,
        time=requested_time
    )

    # Update AgentState
    return {
        **state,
        "pfz_candidates": result.get("pfz_candidates", [])
    }