from ai.agent_state import AgentState
from ai.schemas.location import Location
from ai.schemas.time import TimeContext, TimeSlot

from services.location.place_to_coordinate import get_coordinates
from services.location.pfz_to_coordinate import get_pfz_coordinates


async def general_node(state: AgentState) -> dict:
    return {
        "response": {
            "message": "This is a general fishing-related request."
        },
        "workflow_status": "COMPLETED"
    }


async def safety_node(state: AgentState) -> dict:
    return {
        "response": {
            "message": "This is a safety assessment request."
        },
        "workflow_status": "COMPLETED"
    }


async def planning_node(state: AgentState) -> dict:
    return {
        "response": {
            "message": "This is a fishing trip planning request."
        },
        "workflow_status": "COMPLETED"
    }

async def location_node(state: AgentState) -> dict:
    location = state.get("location")

    # 1. Location already contains coordinates
    #    Example: coordinates sent from frontend/map
    if (
        location
        and location.latitude is not None
        and location.longitude is not None
    ):
        return {
            "location": location,
            "workflow_status": "IN_PROGRESS",
        }

    # 2. User provided a place name
    if location and location.place:
        coordinates = get_coordinates(location.place)

        if (
            coordinates["latitude"] is None
            or coordinates["longitude"] is None
        ):
            return {
                "pending_action": "GET_LOCATION",
                "workflow_status": "WAITING_FOR_USER",
            }

        return {
            "location": Location(
                place=location.place,
                latitude=coordinates["latitude"],
                longitude=coordinates["longitude"],
            ),
            "workflow_status": "IN_PROGRESS",
        }

    # 3. No location available
    return {
        "pending_action": "GET_LOCATION",
        "workflow_status": "WAITING_FOR_USER",
    }

async def time_node(state: AgentState) -> dict:
    time_context = state.get("time_context")

    # Time already resolved
    if time_context and time_context.slots:
        return {
            "time_context": time_context,
            "workflow_status": "IN_PROGRESS",
        }

    # Time is missing
    return {
        "pending_action": "GET_TIME",
        "workflow_status": "WAITING_FOR_USER",
    }

async def pfz_node(state: AgentState) -> dict:
    selected_pfz_id = state.get("selected_pfz_id")

    # User directly specified a PFZ
    if selected_pfz_id:
        try:
            pfz = get_pfz_coordinates(selected_pfz_id)

            return {
                "selected_pfz": pfz,
                "workflow_status": "IN_PROGRESS",
            }

        except ValueError:
            return {
                "pending_action": "SELECT_PFZ",
                "workflow_status": "WAITING_FOR_USER",
            }

    # PFZ candidates already generated
    pfz_candidates = state.get("pfz_candidates", [])

    if pfz_candidates:
        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    # No candidates yet
    return {
        "pending_action": "GENERATE_PFZ_CANDIDATES",
        "workflow_status": "IN_PROGRESS",
    }