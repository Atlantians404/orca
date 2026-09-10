import json

from langgraph.types import interrupt

from ai.agent_state import AgentState
from ai.schemas.location import Location

from ai.configs.config import llm
from ai.prompts.time_prompt import TIME_PROMPT

from ai.agents.general_agent.general_agent import general_agent

from ai.engines.risk_engine.risk_node import risk_engine_node

from services.location.place_to_coordinate import get_coordinates
from services.location.pfz_to_coordinate import get_pfz_coordinates

from services.time.time_parser import (
    build_specific_time,
    build_generic_time,
)

from services.marine_data_sources import get_pfz_candidates


# =========================================================
# DATA COLLECTION
# CHANGE THIS IMPORT IF YOUR FRIEND'S FUNCTION NAME DIFFERS
# =========================================================

from ai.agents.data_collection_agent.data_collection_agent import (
    data_collection_agent,
)


# =========================================================
# ROUTE ENGINE
# CHANGE THIS IMPORT IF YOUR ROUTE ENGINE STRUCTURE DIFFERS
# =========================================================

from ai.engines.route_engine.route_node import (
    route_engine_node,
)


# =========================================================
# CONSTANTS
# =========================================================

DEFAULT_RADIUS_KM = 50.0
MAX_PFZ_CANDIDATES = 20


# =========================================================
# GENERAL NODE
# =========================================================

async def general_node(state: AgentState) -> dict:

    result = await general_agent([
        {
            "role": "user",
            "content": state["prompt"],
        }
    ])

    messages = result["messages"]

    final_message = messages[-1].content

    return {
        "response": {
            "message": final_message,
        },
        "workflow_status": "COMPLETED",
    }


# =========================================================
# SAFETY NODE
# =========================================================

async def safety_node(state: AgentState) -> dict:

    return {
        "response": {
            "message": "This is a safety assessment request.",
        },
        "workflow_status": "COMPLETED",
    }


# =========================================================
# PLANNING NODE
# =========================================================

async def planning_node(state: AgentState) -> dict:

    return {
        "response": {
            "message": "This is a fishing trip planning request.",
        },
        "workflow_status": "IN_PROGRESS",
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

        coordinates = await get_coordinates(
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
        "message": "When would you like to go fishing?",
    })

    # -----------------------------------------------------
    # 3. Extract time using LLM
    # -----------------------------------------------------

    prompt = TIME_PROMPT.format(
        time_input=user_time
    )

    response = await llm.ainvoke(prompt)

    content = response.content.strip()

    # -----------------------------------------------------
    # Remove markdown code fences
    # -----------------------------------------------------

    if content.startswith("```"):

        content = content.replace(
            "```json",
            "",
            1,
        )

        content = content.replace(
            "```",
            "",
            1,
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
    # 1. PFZ already directly selected
    # -----------------------------------------------------

    if selected_pfz_name:

        try:

            pfz = await get_pfz_coordinates(
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
        {},
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
                    "No PFZ zones found.",
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
# DATA COLLECTION NODE
# =========================================================

async def data_collection_node(
    state: AgentState,
) -> dict:

    # -----------------------------------------------------
    # Call friend's Data Collection Agent
    # -----------------------------------------------------

    agent_data = await data_collection_agent(
        location=state.get("location"),
        time_context=state.get("time_context"),
        pfz_candidates=state.get("pfz_candidates", {}),
    )

    return {
        "agent_data": agent_data,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


# =========================================================
# RISK NODE
# Existing Risk Engine
# =====================================================

async def risk_node(
    state: AgentState,
) -> dict:

    result = await risk_engine_node(state)

    return {
        "risk_result": result["risk_result"],
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


# =========================================================
# PFZ SELECTION HITL
# Risk results are shown before user selects
# =========================================================

async def pfz_selection_node(
    state: AgentState,
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
            "workflow_status": "IN_PROGRESS",
        }

    # -----------------------------------------------------
    # 2. Get risk result
    # -----------------------------------------------------

    risk_result = state.get(
        "risk_result",
        {},
    )

    ranked_results = risk_result.get(
        "ranked_results",
        [],
    )

    if not ranked_results:

        return {
            "workflow_status": "COMPLETED",
            "response": {
                "message": "No risk results were available.",
            },
        }

    # -----------------------------------------------------
    # 3. Build UI options
    # -----------------------------------------------------

    pfz_options = []

    for result in ranked_results:

        pfz_name = result.get(
            "pfz_name"
        )

        if not pfz_name:
            continue

        pfz_options.append({
            "pfz_name": pfz_name,
            "risk_score": result.get("risk_score"),
            "risk_level": result.get("risk_level"),
        })

    if not pfz_options:

        return {
            "workflow_status": "COMPLETED",
            "response": {
                "message": "No valid PFZ options were found.",
            },
        }

    # -----------------------------------------------------
    # 4. HITL
    # -----------------------------------------------------

    selected_name = interrupt({
        "action": "SELECT_PFZ",
        "message": (
            "Select a PFZ based on the risk assessment."
        ),
        "options": pfz_options,
    })

    # -----------------------------------------------------
    # 5. Validate input
    # -----------------------------------------------------

    if not isinstance(selected_name, str):

        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    requested_name = (
        selected_name
        .strip()
        .casefold()
    )

    selected_result = None

    for result in ranked_results:

        pfz_name = result.get(
            "pfz_name",
            "",
        )

        if (
            pfz_name
            .strip()
            .casefold()
            == requested_name
        ):

            selected_result = result
            break

    # -----------------------------------------------------
    # 6. Invalid selection
    # -----------------------------------------------------

    if selected_result is None:

        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    # -----------------------------------------------------
    # 7. Find original PFZ candidate
    # -----------------------------------------------------

    candidates = state.get(
        "pfz_candidates",
        {},
    )

    selected_pfz = None

    for candidate in candidates.values():

        candidate_name = candidate.get(
            "name",
            "",
        )

        if (
            candidate_name
            .strip()
            .casefold()
            == requested_name
        ):

            selected_pfz = candidate
            break

    # -----------------------------------------------------
    # 8. Store selected PFZ
    # -----------------------------------------------------

    actual_name = selected_result.get(
        "pfz_name"
    )

    return {
        "selected_pfz_name": actual_name,
        "selected_pfz": selected_pfz or selected_result,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


# =========================================================
# ROUTE NODE
# Existing Route Engine
# =========================================================

async def route_node(
    state: AgentState,
) -> dict:

    result = await route_engine_node(state)

    return {
        "route_result": result.get(
            "route_result"
        ),
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


# =========================================================
# FINAL RESPONSE NODE
# =========================================================

async def final_response_node(
    state: AgentState,
) -> dict:

    risk_result = state.get(
        "risk_result"
    )

    selected_pfz = state.get(
        "selected_pfz"
    )

    route_result = state.get(
        "route_result"
    )

    # -----------------------------------------------------
    # Risk result available
    # -----------------------------------------------------

    if risk_result:

        ranked_results = risk_result.get(
            "ranked_results",
            [],
        )

        # Case 1 / Case 2 / Case 4
        if ranked_results:

            if selected_pfz:

                selected_name = (
                    state.get(
                        "selected_pfz_name"
                    )
                )

                selected_risk = None

                for result in ranked_results:

                    if (
                        result.get("pfz_name", "")
                        .strip()
                        .casefold()
                        == selected_name
                        .strip()
                        .casefold()
                    ):

                        selected_risk = result
                        break

                if selected_risk:

                    message = (
                        f"Selected PFZ: {selected_name}\n"
                        f"Risk Score: "
                        f"{selected_risk.get('risk_score')}\n"
                        f"Risk Level: "
                        f"{selected_risk.get('risk_level')}"
                    )

                else:

                    message = (
                        f"Selected PFZ: {selected_name}"
                    )

            else:

                message = (
                    "Risk assessment completed."
                )

        # Case 3
        else:

            message = (
                "Risk assessment completed for "
                "the requested PFZs and times."
            )

    else:

        message = (
            "Your ORCA request has been completed."
        )

    # -----------------------------------------------------
    # Add route information
    # -----------------------------------------------------

    if route_result:

        message += (
            "\n\nRoute generation completed."
        )

    return {
        "response": {
            "message": message,
        },
        "pending_action": None,
        "workflow_status": "COMPLETED",
    }