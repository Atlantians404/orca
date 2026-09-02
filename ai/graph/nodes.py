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

from langgraph.types import interrupt

async def location_node(state: AgentState) -> dict:
    location = state.get("location")

    # Location already available
    if (
        location
        and location.latitude is not None
        and location.longitude is not None
    ):
        return {
            "location": location,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # Place name provided → resolve it
    if location and location.place:
        coordinates = get_coordinates(location.place)

        if (
            coordinates["latitude"] is not None
            and coordinates["longitude"] is not None
        ):
            resolved_location = Location(
                place=location.place,
                latitude=coordinates["latitude"],
                longitude=coordinates["longitude"],
            )

            return {
                "location": resolved_location,
                "pending_action": None,
                "workflow_status": "IN_PROGRESS",
            }

    # Missing/invalid location → pause
    user_location = interrupt({
        "action": "GET_LOCATION",
        "message": "Please provide your current location.",
        "options": [
            "Select location from map",
            "Enter place name",
            "Enter latitude and longitude",
        ],
    })

    # Graph resumes here after Command(resume=...)
    return {
        "location": Location(**user_location),
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


from langgraph.types import interrupt


async def time_node(state: AgentState) -> dict:
    time_context = state.get("time_context")

    # Time already available
    if time_context and time_context.slots:
        return {
            "time_context": time_context,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # Missing time → pause
    user_time = interrupt({
        "action": "GET_TIME",
        "message": "Please provide your fishing time.",
        "options": [
            "Specific time",
            "Morning",
            "Afternoon",
            "Evening",
        ],
    })

    return {
        "time_context": TimeContext(**user_time),
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
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