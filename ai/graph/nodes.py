import json

from langgraph.types import interrupt

from ai.agent_state import AgentState
from ai.schemas.location import Location

from ai.configs.config import llm
from ai.prompts.time_prompt import TIME_PROMPT

from ai.agents.general_agent.general_agent import general_agent

from services.location.place_to_coordinate import get_coordinates
from services.location.pfz_to_coordinate import get_pfz_coordinates

from services.time.time_parser import (
    build_specific_time,
    build_generic_time,
)

from services.marine_data_sources import get_pfz_candidates


DEFAULT_RADIUS_KM = 50.0
MAX_PFZ_CANDIDATES = 20


# =========================================================
# GENERAL NODE
# =========================================================

async def general_node(state: AgentState) -> dict:

    result = await general_agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": state["prompt"]
            }
        ]
    })

    messages = result["messages"]

    final_message = messages[-1].content

    return {
        "response": {
            "message": final_message
        },
        "workflow_status": "COMPLETED"
    }


# =========================================================
# SAFETY NODE
# =========================================================

async def safety_node(state: AgentState) -> dict:

    return {
        "response": {
            "message": "This is a safety assessment request."
        },
        "workflow_status": "COMPLETED"
    }


# =========================================================
# PLANNING NODE
# =========================================================

async def planning_node(state: AgentState) -> dict:

    return {
        "response": {
            "message": "This is a fishing trip planning request."
        },
        "workflow_status": "COMPLETED"
    }


# =========================================================
# LOCATION NODE
# =========================================================

async def location_node(state: AgentState) -> dict:

    location = state.get("location")

    # -----------------------------------------------------
    # 1. Location already available
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 2. Place name provided → resolve coordinates
    # -----------------------------------------------------

    if location and location.place:

        coordinates = get_coordinates(
            location.place
        )

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

    # -----------------------------------------------------
    # 3. Missing location → interrupt
    # -----------------------------------------------------

    user_location = interrupt({
        "action": "GET_LOCATION",
        "message": "Please provide your current location.",
        "options": [
            "Select location from map",
            "Enter place name",
            "Enter latitude and longitude",
        ],
    })

    # -----------------------------------------------------
    # 4. Resume after user provides location
    # -----------------------------------------------------

    return {
        "location": Location(**user_location),
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


# =========================================================
# TIME NODE
# =========================================================

async def time_node(state: AgentState) -> dict:

    time_context = state.get("time_context")

    # -----------------------------------------------------
    # 1. Time already available
    # -----------------------------------------------------

    if time_context and time_context.slots:

        return {
            "time_context": time_context,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # -----------------------------------------------------
    # 2. Ask user for time
    # -----------------------------------------------------

    user_time = interrupt({
        "action": "GET_TIME",
        "message": "When would you like to go fishing?"
    })

    # -----------------------------------------------------
    # 3. Extract time using LLM
    # -----------------------------------------------------

    prompt = TIME_PROMPT.format(
        time_input=user_time
    )

    response = await llm.ainvoke(prompt)

    content = response.content.strip()

    # Remove markdown code fences
    if content.startswith("```"):

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()

    extracted = json.loads(content)

    time_type = extracted.get(
        "time_type"
    )

    # -----------------------------------------------------
    # 4. Specific time
    # -----------------------------------------------------

    if time_type == "specific":

        time = extracted.get(
            "time"
        )

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

    # -----------------------------------------------------
    # 5. Generic time
    # -----------------------------------------------------

    if time_type == "generic":

        period = extracted.get(
            "period"
        )

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

    # -----------------------------------------------------
    # 6. Time missing / unclear
    # -----------------------------------------------------

    return {
        "pending_action": "GET_TIME",
        "workflow_status": "WAITING_FOR_USER",
    }


# =========================================================
# PFZ NODE
# =========================================================

async def pfz_node(state: AgentState) -> dict:

    selected_pfz_name = state.get(
        "selected_pfz_name"
    )

    # -----------------------------------------------------
    # 1. User directly specified PFZ name
    # -----------------------------------------------------

    if selected_pfz_name:

        try:

            pfz = get_pfz_coordinates(
                selected_pfz_name
            )

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

    # -----------------------------------------------------
    # 2. PFZ candidates already generated
    # -----------------------------------------------------

    pfz_candidates = state.get(
        "pfz_candidates"
    )

    if pfz_candidates:

        return {
            "pfz_candidates": pfz_candidates,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # -----------------------------------------------------
    # 3. Location required
    # -----------------------------------------------------

    location = state.get(
        "location"
    )

    if not location:

        return {
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    # -----------------------------------------------------
    # 4. Determine search radius
    # -----------------------------------------------------

    distance_km = state.get(
        "distance_km"
    )

    if distance_km is None:

        distance_km = DEFAULT_RADIUS_KM

    # -----------------------------------------------------
    # 5. Generate PFZ candidates
    # -----------------------------------------------------

    result = get_pfz_candidates(
        latitude=location.latitude,
        longitude=location.longitude,
        radius_km=distance_km,
        number_of_zones=MAX_PFZ_CANDIDATES,
    )

    candidates = result.get(
        "pfz_zones",
        {}
    )

    # -----------------------------------------------------
    # 6. No candidates
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 7. Store candidates
    # -----------------------------------------------------

    return {
        "pfz_candidates": candidates,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


# =========================================================
# PFZ SELECTION NODE
# =========================================================

async def pfz_selection_node(
    state: AgentState
) -> dict:

    # -----------------------------------------------------
    # 1. PFZ already selected
    # -----------------------------------------------------

    selected_pfz = state.get(
        "selected_pfz"
    )

    if selected_pfz:

        return {
            "pending_action": None,
            "workflow_status": "IN_PROGRESS"
        }

    # -----------------------------------------------------
    # 2. Get candidates
    # -----------------------------------------------------

    candidates = state.get(
        "pfz_candidates",
        {}
    )

    if not candidates:

        return {
            "workflow_status": "COMPLETED"
        }

    # -----------------------------------------------------
    # 3. Extract actual PFZ names
    # -----------------------------------------------------

    pfz_names = []

    for candidate in candidates.values():

        name = candidate.get(
            "name"
        )

        if name:
            pfz_names.append(name)

    # -----------------------------------------------------
    # 4. Ask user to select PFZ
    # -----------------------------------------------------

    selected_name = interrupt({
        "action": "SELECT_PFZ",
        "message": "Please select a PFZ.",
        "options": pfz_names
    })

    # -----------------------------------------------------
    # 5. Validate user selection
    # -----------------------------------------------------

    selected_name = (
        selected_name
        .strip()
        .lower()
    )

    selected_pfz = None

    for candidate in candidates.values():

        candidate_name = candidate.get(
            "name",
            ""
        )

        if (
            candidate_name
            .strip()
            .lower()
            == selected_name
        ):

            selected_pfz = candidate
            break

    # -----------------------------------------------------
    # 6. Invalid PFZ selection
    # -----------------------------------------------------

    if selected_pfz is None:

        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER"
        }

    # -----------------------------------------------------
    # 7. Store selected PFZ
    # -----------------------------------------------------

    actual_name = selected_pfz.get(
        "name"
    )

    return {
        "selected_pfz_name": actual_name,
        "selected_pfz": selected_pfz,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS"
    }


# =========================================================
# SELECT PFZ HELPER
# =========================================================

def select_pfz(
    pfz_candidates: dict,
    pfz_name: str
) -> dict | None:
    """
    Select a PFZ using its actual name.

    Example:

        select_pfz(
            candidates,
            "Pondicherry"
        )
    """

    if not pfz_candidates:
        return None

    requested_name = (
        pfz_name
        .strip()
        .lower()
    )

    for pfz in pfz_candidates.values():

        candidate_name = pfz.get(
            "name",
            ""
        )

        if (
            candidate_name
            .strip()
            .lower()
            == requested_name
        ):

            return pfz

    return None