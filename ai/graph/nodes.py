import json

from ai.agent_state import AgentState
from ai.schemas.location import Location
from ai.schemas.time import TimeContext, TimeSlot

from services.location.place_to_coordinate import get_coordinates
from services.location.pfz_to_coordinate import get_pfz_coordinates

from langgraph.types import interrupt

from ai.configs.config import llm
from ai.prompts.time_prompt import TIME_PROMPT

from services.time.time_parser import (
    build_specific_time,
    build_generic_time,
)

from services.marine_data_sources import get_pfz_candidates


DEFAULT_RADIUS_KM = 50.0
MAX_PFZ_CANDIDATES = 20

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

async def time_node(state: AgentState) -> dict:

    time_context = state.get("time_context")

    # -----------------------------------------
    # Time already exists
    # -----------------------------------------

    if time_context and time_context.slots:
        return {
            "time_context": time_context,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # -----------------------------------------
    # Ask user naturally
    # -----------------------------------------

    user_time = interrupt({
        "action": "GET_TIME",
        "message": "When would you like to go fishing?"
    })

    # -----------------------------------------
    # AI extracts time information
    # -----------------------------------------

    prompt = TIME_PROMPT.format(
        time_input=user_time
    )

    response = await llm.ainvoke(prompt)

    content = response.content.strip()

    # Remove markdown fences if model returns them
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()



    extracted = json.loads(content)

    time_type = extracted.get("time_type")

    # -----------------------------------------
    # Specific time
    # -----------------------------------------

    if time_type == "specific":

        time = extracted.get("time")

        if not time:
            return {
                "pending_action": "GET_TIME",
                "workflow_status": "WAITING_FOR_USER",
            }

        resolved_time = build_specific_time(
            date_expression=extracted.get("date"),
            time=time,
        )

        return {
            "time_context": resolved_time,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # -----------------------------------------
    # Generic time
    # -----------------------------------------

    if time_type == "generic":

        period = extracted.get("period")

        if not period:
            return {
                "pending_action": "GET_TIME",
                "workflow_status": "WAITING_FOR_USER",
            }

        resolved_time = build_generic_time(
            date_expression=extracted.get("date"),
            period=period,
        )

        return {
            "time_context": resolved_time,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # -----------------------------------------
    # Time missing / unclear
    # -----------------------------------------

    return {
        "pending_action": "GET_TIME",
        "workflow_status": "WAITING_FOR_USER",
    }

async def pfz_node(state: AgentState) -> dict:
    selected_pfz_name = state.get("selected_pfz_name")

    # ---------------------------------------------------------
    # 1. User directly specified a PFZ
    # ---------------------------------------------------------
    if selected_pfz_name:
        try:
            pfz = get_pfz_coordinates(selected_pfz_name)

            return {
                "selected_pfz": pfz,
                "pending_action": None,
                "workflow_status": "IN_PROGRESS",
            }

        except ValueError:
            return {
                "pending_action": "SELECT_PFZ",
                "workflow_status": "WAITING_FOR_USER",
            }

    # ---------------------------------------------------------
    # 2. PFZ candidates already generated
    # ---------------------------------------------------------
    pfz_candidates = state.get("pfz_candidates")

    if pfz_candidates:
        return {
            "pfz_candidates": pfz_candidates,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # ---------------------------------------------------------
    # 3. Location is required for candidate generation
    # ---------------------------------------------------------
    location = state.get("location")

    if not location:
        return {
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    # ---------------------------------------------------------
    # 4. Determine search radius
    # ---------------------------------------------------------
    distance_km = state.get("distance_km")

    if distance_km is None:
        distance_km = DEFAULT_RADIUS_KM

    # ---------------------------------------------------------
    # 5. Generate PFZ candidates
    # ---------------------------------------------------------
    result = get_pfz_candidates(
        latitude=location.latitude,
        longitude=location.longitude,
        radius_km=distance_km,
        number_of_zones=MAX_PFZ_CANDIDATES,
    )

    candidates = result.get("pfz_zones", {})

    # ---------------------------------------------------------
    # 6. No candidates found
    # ---------------------------------------------------------
    if not candidates:
        return {
            "pfz_candidates": {},
            "workflow_status": "COMPLETED",
            "response": {
                "message": result.get(
                    "message",
                    "No PFZ zones found."
                )
            },
        }

    # ---------------------------------------------------------
    # 7. Store candidates in AgentState
    # ---------------------------------------------------------
    return {
        "pfz_candidates": candidates,
        "workflow_status": "IN_PROGRESS",
    }