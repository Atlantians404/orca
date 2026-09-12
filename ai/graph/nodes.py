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

    # Location already contains coordinates.
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

    # Resolve place name to coordinates.
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

    # Ask user for location.
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

    # Time already resolved.
    if time_context and time_context.slots:
        return {
            "time_context": time_context,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # Ask user for fishing time.
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

    # Specific time.
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

    # Generic time such as morning/evening.
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

    # If a PFZ name was already selected, resolve its coordinates.
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

    # PFZ candidates already exist.
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
    """
    Ask the user to select a PFZ.

    The important part here is that the complete PFZ information
    is preserved in the HITL options, including coordinates.
    """

    selected_pfz = state.get("selected_pfz")

    # PFZ already selected.
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

    # Original PFZ candidates.
    candidates = state.get("pfz_candidates", {})

    if isinstance(candidates, dict):
        candidate_list = list(candidates.values())

    elif isinstance(candidates, list):
        candidate_list = candidates

    else:
        candidate_list = []

    pfz_options = []

    for result in ranked_results:
        pfz_name = result.get("pfz_name")

        if not pfz_name:
            continue

        # Risk result times.
        times = result.get("times", [])

        # Try to get coordinates from the risk result first.
        latitude = result.get("latitude")
        longitude = result.get("longitude")

        # If not present, search the original PFZ candidate.
        if latitude is None or longitude is None:
            for candidate in candidate_list:
                if not isinstance(candidate, dict):
                    continue

                candidate_name = candidate.get(
                    "name",
                    candidate.get("pfz_name", ""),
                )

                if (
                    candidate_name
                    and candidate_name.strip().casefold()
                    == pfz_name.strip().casefold()
                ):
                    latitude = candidate.get("latitude")
                    longitude = candidate.get("longitude")

                    # Support nested coordinate structures if present.
                    coordinates = candidate.get("coordinates")

                    if isinstance(coordinates, dict):
                        if latitude is None:
                            latitude = coordinates.get("latitude")

                        if longitude is None:
                            longitude = coordinates.get("longitude")

                    break

        # Build the HITL option.
        option = {
            "pfz_name": pfz_name,
            "latitude": latitude,
            "longitude": longitude,
            "times": times,
        }

        pfz_options.append(option)

    if not pfz_options:
        return {
            "workflow_status": "COMPLETED",
            "response": {
                "message": "No valid PFZ options were found.",
            },
        }

    # Ask user to select PFZ.
    selected_value = interrupt(
        {
            "action": "SELECT_PFZ",
            "message": "Select a PFZ based on the risk assessment.",
            "options": pfz_options,
        }
    )

    # ---------------------------------------------------------
    # Support both:
    #
    # "Coromandel"
    #
    # and:
    #
    # {
    #     "pfz_name": "Coromandel",
    #     "latitude": ...,
    #     "longitude": ...
    # }
    # ---------------------------------------------------------
    if isinstance(selected_value, str):
        requested_name = selected_value.strip()

    elif isinstance(selected_value, dict):
        requested_name = str(
            selected_value.get("pfz_name", "")
        ).strip()

    else:
        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    if not requested_name:
        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    requested_name_normalized = requested_name.casefold()

    selected_result = None

    # Find the selected PFZ inside risk results.
    for result in ranked_results:
        pfz_name = result.get("pfz_name", "")

        if (
            pfz_name.strip().casefold()
            == requested_name_normalized
        ):
            selected_result = result
            break

    if selected_result is None:
        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    # ---------------------------------------------------------
    # Find the original PFZ candidate.
    # ---------------------------------------------------------
    selected_pfz = None

    for candidate in candidate_list:
        if not isinstance(candidate, dict):
            continue

        candidate_name = candidate.get(
            "name",
            candidate.get("pfz_name", ""),
        )

        if (
            candidate_name
            and candidate_name.strip().casefold()
            == requested_name_normalized
        ):
            selected_pfz = candidate
            break

    # ---------------------------------------------------------
    # If original candidate wasn't found, use the selected
    # risk result as the PFZ object.
    # ---------------------------------------------------------
    if selected_pfz is None:
        selected_pfz = selected_result.copy()

    # ---------------------------------------------------------
    # Make sure coordinates exist.
    #
    # If they're still missing, use the PFZ coordinate service.
    # ---------------------------------------------------------
    latitude = selected_pfz.get("latitude")
    longitude = selected_pfz.get("longitude")

    if latitude is None or longitude is None:
        coordinates = selected_pfz.get("coordinates")

        if isinstance(coordinates, dict):
            latitude = coordinates.get("latitude")
            longitude = coordinates.get("longitude")

    if latitude is None or longitude is None:
        try:
            resolved_pfz = await get_pfz_coordinates(
                selected_result.get("pfz_name")
            )

            if isinstance(resolved_pfz, dict):
                if latitude is None:
                    latitude = resolved_pfz.get("latitude")

                if longitude is None:
                    longitude = resolved_pfz.get("longitude")

                # Preserve useful coordinate information.
                if selected_pfz is None:
                    selected_pfz = resolved_pfz

        except (ValueError, KeyError, TypeError):
            pass

    # Add coordinates to selected PFZ if available.
    if latitude is not None:
        selected_pfz["latitude"] = latitude

    if longitude is not None:
        selected_pfz["longitude"] = longitude

    actual_name = selected_result.get("pfz_name")

    return {
        "selected_pfz_name": actual_name,
        "selected_pfz": selected_pfz,

        # IMPORTANT:
        # Preserve the original risk result.
        "risk_result": risk_result,

        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


async def route_node(state: AgentState) -> dict:
    """
    Run the route engine.

    route_result is kept separate from risk_result.
    """

    result = await route_engine_node(state)

    return {
        "route_result": result.get("route_result"),
        "pending_action": None,
        "workflow_status": result.get(
            "workflow_status",
            "IN_PROGRESS",
        ),
    }


async def final_response_node(state: AgentState) -> dict:
    """
    Build the final response using:

    - selected PFZ
    - original PFZ risk result
    - route result
    """

    risk_result = state.get("risk_result")
    selected_pfz_name = state.get("selected_pfz_name")
    selected_pfz = state.get("selected_pfz")
    route_result = state.get("route_result")

    lines = []

    # ---------------------------------------------------------
    # Selected PFZ
    # ---------------------------------------------------------
    if selected_pfz_name:
        lines.append(
            f"Selected PFZ: {selected_pfz_name}"
        )

    # ---------------------------------------------------------
    # PFZ coordinates
    # ---------------------------------------------------------
    if selected_pfz:
        latitude = selected_pfz.get("latitude")
        longitude = selected_pfz.get("longitude")

        if latitude is not None and longitude is not None:
            lines.append(
                f"PFZ Location: {latitude}, {longitude}"
            )

    # ---------------------------------------------------------
    # Risk assessment
    # ---------------------------------------------------------
    if risk_result and selected_pfz_name:
        ranked_results = risk_result.get(
            "ranked_results",
            [],
        )

        selected_risk = None

        for result in ranked_results:
            pfz_name = result.get(
                "pfz_name",
                "",
            )

            if (
                pfz_name.strip().casefold()
                == selected_pfz_name.strip().casefold()
            ):
                selected_risk = result
                break

        if selected_risk:
            risk_times = selected_risk.get(
                "times",
                [],
            )

            # Only display Risk Assessment if there
            # is actually something to show.
            if risk_times:
                lines.append("")
                lines.append("Risk Assessment:")

                for time_result in risk_times:
                    if not isinstance(time_result, dict):
                        continue

                    time_value = time_result.get(
                        "time",
                        "Unknown time",
                    )

                    risk_score = time_result.get(
                        "risk_score",
                        "N/A",
                    )

                    risk_level = time_result.get(
                        "risk_level",
                        "UNKNOWN",
                    )

                    lines.append(
                        f"- {time_value}: "
                        f"{risk_score} "
                        f"({risk_level})"
                    )

    # ---------------------------------------------------------
    # Route result
    # ---------------------------------------------------------
    if route_result:
        safe_route = route_result.get(
            "safe_route"
        )

        candidate_routes = route_result.get(
            "candidate_routes",
            [],
        )

        lines.append("")

        if safe_route:
            lines.append(
                "Recommended Route:"
            )

            lines.append(
                f"- Route ID: "
                f"{safe_route.get('route_id')}"
            )

            distance_km = safe_route.get(
                "distance_km"
            )

            if distance_km is not None:
                lines.append(
                    f"- Distance: "
                    f"{distance_km:.2f} km"
                )

            lines.append(
                f"- Route Risk: "
                f"{safe_route.get('risk_score')}"
            )

            lines.append(
                f"- Status: "
                f"{'SAFE' if safe_route.get('safe') else 'UNSAFE'}"
            )

        elif candidate_routes:
            lines.append(
                "No safe route was found."
            )

            lines.append(
                f"Candidate routes evaluated: "
                f"{len(candidate_routes)}"
            )

        else:

            lines.append(

                "No route could be generated."

            )

            route_error = route_result.get("error")

            if route_error:

                lines.append(

            f"Route Engine Error: {route_error}"

        )

    # ---------------------------------------------------------
    # Fallback
    # ---------------------------------------------------------
    if not lines:
        lines.append(
            "Your ORCA request has been completed."
        )

    return {
        "response": {
            "message": "\n".join(lines),
        },
        "pending_action": None,
        "workflow_status": "COMPLETED",
    }