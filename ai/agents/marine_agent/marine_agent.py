from typing import Any

from services.marine_data_sources import (
    get_pfz_candidates,
    select_pfz
)

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
            "pfz_candidates": [],
            "selected_pfz": None
        }

    if location.latitude is None or location.longitude is None:
        return {
            **state,
            "pfz_candidates": [],
            "selected_pfz": None
        }

    if time_context is None or not time_context.slots:
        return {
            **state,
            "pfz_candidates": [],
            "selected_pfz": None
        }


    # Get PFZ candidates
    result = get_pfz_candidates(
    latitude=location.latitude,
    longitude=location.longitude
    )

    # Extract candidates
    pfz_candidates = result.get("pfz_candidates", [])

    # Select a specific PFZ if requested
    selected_pfz = None

    requested_pfz_id = state.get("selected_pfz_id")

    if requested_pfz_id:
        selected_pfz = select_pfz(
            pfz_candidates,
            requested_pfz_id
        )

    # Update AgentState
    return {
        **state,
        "pfz_candidates": pfz_candidates,
        "selected_pfz": selected_pfz
    }