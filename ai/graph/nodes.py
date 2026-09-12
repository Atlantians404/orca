import json

from langgraph.types import interrupt

from ai.agent_state import AgentState
from ai.schemas.location import Location
from ai.configs.config import llm
from ai.prompts.time_prompt import TIME_PROMPT

from ai.agents.general_agent.general_agent import general_agent
from ai.engines.risk_engine.risk_node import risk_engine_node
from ai.engines.data_collection_engine.data_collection_engine import (
    data_collection_engine,
)
from ai.engines.route_engine.route_node import (
    route_node as route_engine_node,
)

from services.location.place_to_coordinate import get_coordinates
from services.location.pfz_to_coordinate import get_pfz_coordinates
from services.time.time_parser import (
    build_specific_time,
    build_generic_time,
)
from services.marine_data_sources import get_pfz_candidates


DEFAULT_RADIUS_KM = 50.0
MAX_PFZ_CANDIDATES = 20


async def general_node(state: AgentState) -> dict:
    result = await general_agent(
        [
            {
                "role": "user",
                "content": state["prompt"],
            }
        ]
    )

    messages = result["messages"]
    final_message = messages[-1].content

    return {
        "response": {
            "message": final_message,
        },
        "workflow_status": "COMPLETED",
    }


async def safety_node(state: AgentState) -> dict:
    return {
        "response": {
            "message": "This is a safety assessment request.",
        },
        "workflow_status": "COMPLETED",
    }


async def planning_node(state: AgentState) -> dict:
    return {
        "response": {
            "message": "This is a fishing trip planning request.",
        },
        "workflow_status": "IN_PROGRESS",
    }


async def location_node(state: AgentState) -> dict:
    location = state.get("location")

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

    if location and location.place:
        coordinates = await get_coordinates(location.place)

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

    user_location = interrupt(
        {
            "action": "GET_LOCATION",
            "message": "Please provide your current location.",
            "options": [
                "Select location from map",
                "Enter place name",
                "Enter latitude and longitude",
            ],
        }
    )

    return {
        "location": Location(**user_location),
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


async def time_node(state: AgentState) -> dict:
    time_context = state.get("time_context")

    if time_context and time_context.slots:
        return {
            "time_context": time_context,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    user_time = interrupt(
        {
            "action": "GET_TIME",
            "message": "When would you like to go fishing?",
        }
    )

    prompt = TIME_PROMPT.format(time_input=user_time)

    response = await llm.ainvoke(prompt)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "", 1)
        content = content.strip()

    extracted = json.loads(content)

    time_type = extracted.get("time_type")

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

    return {
        "pending_action": "GET_TIME",
        "workflow_status": "WAITING_FOR_USER",
    }


async def pfz_node(state: AgentState) -> dict:
    selected_pfz_name = state.get("selected_pfz_name")

    if selected_pfz_name:
        try:
            pfz = await get_pfz_coordinates(selected_pfz_name)

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

    pfz_candidates = state.get("pfz_candidates")

    if pfz_candidates:
        return {
            "pfz_candidates": pfz_candidates,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    location = state.get("location")

    if not location:
        return {
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    distance_km = state.get("distance_km")

    if distance_km is None:
        distance_km = DEFAULT_RADIUS_KM

    result = get_pfz_candidates(
        latitude=location.latitude,
        longitude=location.longitude,
        radius_km=distance_km,
        number_of_zones=MAX_PFZ_CANDIDATES,
    )

    candidates = result.get("pfz_zones", {})

    if not candidates:
        return {
            "pfz_candidates": {},
            "workflow_status": "COMPLETED",
            "response": {
                "message": result.get(
                    "message",
                    "No PFZ zones found.",
                ),
            },
        }

    return {
        "pfz_candidates": candidates,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


async def data_collection_node(state: AgentState) -> dict:
    pfz_candidates = state.get("pfz_candidates", {})

    if isinstance(pfz_candidates, dict):
        pfz_list = list(pfz_candidates.values())
    elif isinstance(pfz_candidates, list):
        pfz_list = pfz_candidates
    else:
        pfz_list = []

    collection_state = {
        **state,
        "pfz_candidates": pfz_list,
    }

    updated_state = await data_collection_engine(collection_state)

    return {
        "agent_data": updated_state.get("agent_data", {}),
        "workflow_status": "IN_PROGRESS",
    }


async def risk_node(state: AgentState) -> dict:
    result = await risk_engine_node(state)

    return {
        "risk_result": result["risk_result"],
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


async def pfz_selection_node(state: AgentState) -> dict:
    selected_pfz = state.get("selected_pfz")

    if selected_pfz:
        return {
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    risk_result = state.get("risk_result", {})
    ranked_results = risk_result.get("ranked_results", [])

    if not ranked_results:
        return {
            "workflow_status": "COMPLETED",
            "response": {
                "message": "No risk results were available.",
            },
        }

    pfz_options = []

    for result in ranked_results:
        pfz_name = result.get("pfz_name")

        if not pfz_name:
            continue

        times = result.get("times", [])

        pfz_options.append(
            {
                "pfz_name": pfz_name,
                "times": times,
            }
        )

    if not pfz_options:
        return {
            "workflow_status": "COMPLETED",
            "response": {
                "message": "No valid PFZ options were found.",
            },
        }

    selected_name = interrupt(
        {
            "action": "SELECT_PFZ",
            "message": "Select a PFZ based on the risk assessment.",
            "options": pfz_options,
        }
    )

    if not isinstance(selected_name, str):
        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    requested_name = selected_name.strip().casefold()

    selected_result = None

    for result in ranked_results:
        pfz_name = result.get("pfz_name", "")

        if pfz_name.strip().casefold() == requested_name:
            selected_result = result
            break

    if selected_result is None:
        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    candidates = state.get("pfz_candidates", {})

    selected_pfz = None

    if isinstance(candidates, dict):
        for candidate in candidates.values():
            candidate_name = candidate.get("name", "")

            if candidate_name.strip().casefold() == requested_name:
                selected_pfz = candidate
                break

    actual_name = selected_result.get("pfz_name")

    return {
        "selected_pfz_name": actual_name,
        "selected_pfz": selected_pfz or selected_result,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


async def route_node(state: AgentState) -> dict:
    result = await route_engine_node(state)

    return {
        "route_result": result.get("route_result"),
        "risk_result": result.get("risk_result"),
        "pending_action": None,
        "workflow_status": result.get(
            "workflow_status",
            "IN_PROGRESS",
        ),
    }


async def final_response_node(state: AgentState) -> dict:
    risk_result = state.get("risk_result")
    selected_pfz = state.get("selected_pfz")
    selected_pfz_name = state.get("selected_pfz_name")
    route_result = state.get("route_result")

    if risk_result:
        ranked_results = risk_result.get("ranked_results", [])

        if selected_pfz and selected_pfz_name:
            selected_risk = None

            for result in ranked_results:
                if (
                    result.get("pfz_name", "").strip().casefold()
                    == selected_pfz_name.strip().casefold()
                ):
                    selected_risk = result
                    break

            if selected_risk:
                message = (
                    f"Selected PFZ: {selected_pfz_name}\n"
                    f"Risk Assessment:\n"
                )

                for time_result in selected_risk.get("times", []):
                    message += (
                        f"- {time_result.get('time')}: "
                        f"{time_result.get('risk_score')} "
                        f"({time_result.get('risk_level')})\n"
                    )
            else:
                message = f"Selected PFZ: {selected_pfz_name}"

        elif ranked_results:
            message = "Risk assessment completed."

        else:
            message = (
                "Risk assessment completed for "
                "the requested PFZs and times."
            )

    else:
        message = "Your ORCA request has been completed."

    if route_result:
        message += "\n\nRoute generation completed."

    return {
        "response": {
            "message": message,
        },
        "pending_action": None,
        "workflow_status": "COMPLETED",
    }