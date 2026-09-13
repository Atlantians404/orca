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

from ai.schemas.agent_response import (
    AgentResponse,
    MapData,
    PFZData,
    RiskData,
    RouteData,
    WaypointData,
)


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
        "selected_pfz_name": requested_name,
        "selected_pfz": selected_pfz,
        "risk_result": risk_result,

        # Preserve route requirement for the conditional edge
        "route_required": state.get("route_required", False),

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


def final_response_node(state: AgentState) -> dict:
    """
    Build the final structured response after PFZ selection
    and optional route generation.
    """

    selected_pfz = state.get("selected_pfz") or {}
    risk_result = state.get("risk_result") or {}
    route_result = state.get("route_result")

    # =========================================================
    # PFZ DATA
    # =========================================================

    pfz_name = (
        selected_pfz.get("name")
        or state.get("selected_pfz_name")
        or "Unknown PFZ"
    )

    pfz_latitude = selected_pfz.get("latitude")
    pfz_longitude = selected_pfz.get("longitude")
    pfz_distance = selected_pfz.get("distance_from_source_km")

    pfz_data = None

    if pfz_latitude is not None and pfz_longitude is not None:
        pfz_data = PFZData(
            name=pfz_name,
            latitude=float(pfz_latitude),
            longitude=float(pfz_longitude),
            distance_from_source_km=(
                float(pfz_distance)
                if pfz_distance is not None
                else None
            ),
        )

    # =========================================================
    # RISK DATA
    # =========================================================

    risk_score = None
    risk_level = "UNKNOWN"

    ranked_results = risk_result.get(
        "ranked_results",
        []
    )

    for result in ranked_results:

        result_name = (
            result.get("pfz_name")
            or result.get("name")
        )

        if result_name == pfz_name:

            times = result.get(
                "times",
                []
            )

            if times:

                risk_data = times[0]

                risk_score = risk_data.get(
                    "risk_score"
                )

                risk_level = (
                    risk_data.get("risk_level")
                    or risk_data.get("risk")
                    or "UNKNOWN"
                )

            break

    risk_model = None

    if risk_score is not None:
        risk_model = RiskData(
            score=float(risk_score),
            level=str(risk_level),
        )

    # =========================================================
    # ROUTE DATA
    # =========================================================

    route_model = None
    map_model = None

    if route_result:

        # -----------------------------------------------------
        # Get recommended / safe route
        #
        # Route engine returns:
        #
        # {
        #     "candidate_routes": [...],
        #     "safe_route": {...}
        # }
        # -----------------------------------------------------

        recommended_route = route_result.get(
            "safe_route"
        )

        if recommended_route:

            # -------------------------------------------------
            # ROUTE BASIC DATA
            # -------------------------------------------------

            route_id = recommended_route.get(
                "route_id",
                "UNKNOWN"
            )

            distance_km = recommended_route.get(
                "distance_km",
                0.0
            )

            route_risk_score = recommended_route.get(
                "risk_score",
                0.0
            )

            safe = recommended_route.get(
                "safe",
                False
            )

            # -------------------------------------------------
            # WAYPOINTS
            # -------------------------------------------------

            waypoint_models = []

            for waypoint in recommended_route.get(
                "waypoints",
                []
            ):

                latitude = waypoint.get(
                    "latitude"
                )

                longitude = waypoint.get(
                    "longitude"
                )

                if latitude is None or longitude is None:
                    continue

                waypoint_models.append(
                    WaypointData(
                        latitude=float(latitude),
                        longitude=float(longitude),
                        risk_score=(
                            float(waypoint["risk_score"])
                            if waypoint.get("risk_score") is not None
                            else None
                        ),
                        safe=(
                            bool(waypoint["safe"])
                            if waypoint.get("safe") is not None
                            else None
                        ),
                    )
                )

            # -------------------------------------------------
            # GEOJSON
            # -------------------------------------------------

            geojson = recommended_route.get(
                "geojson"
            )

            # -------------------------------------------------
            # BUILD ROUTE MODEL
            # -------------------------------------------------

            route_model = RouteData(
                route_id=str(route_id),
                distance_km=float(distance_km),
                risk_score=float(route_risk_score),
                safe=bool(safe),
                waypoints=waypoint_models,
                geojson=geojson,
            )

            # -------------------------------------------------
            # MAP DATA
            #
            # Frontend coordinates:
            #
            # [longitude, latitude]
            # -------------------------------------------------

            coordinates = []

            for waypoint in recommended_route.get(
                "waypoints",
                []
            ):

                latitude = waypoint.get(
                    "latitude"
                )

                longitude = waypoint.get(
                    "longitude"
                )

                if latitude is None or longitude is None:
                    continue

                coordinates.append(
                    [
                        float(longitude),
                        float(latitude),
                    ]
                )

            # -------------------------------------------------
            # Prefer GeoJSON coordinates
            # -------------------------------------------------

            if geojson:

                geometry = geojson.get(
                    "geometry",
                    {}
                )

                geojson_coordinates = geometry.get(
                    "coordinates"
                )

                if geojson_coordinates:
                    coordinates = geojson_coordinates

            map_model = MapData(
                coordinates=coordinates
            )

    # =========================================================
    # BUILD HUMAN-READABLE MESSAGE
    # =========================================================

    message_lines = [
        f"Selected PFZ: {pfz_name}"
    ]

    # ---------------------------------------------------------
    # PFZ LOCATION
    # ---------------------------------------------------------

    if (
        pfz_latitude is not None
        and pfz_longitude is not None
    ):
        message_lines.append(
            f"PFZ Location: "
            f"{pfz_latitude}, "
            f"{pfz_longitude}"
        )

    # ---------------------------------------------------------
    # RISK
    # ---------------------------------------------------------

    if risk_model:

        message_lines.extend(
            [
                "",
                "Risk Assessment:",
                (
                    f"- Risk: "
                    f"{risk_model.score:.2f} "
                    f"({risk_model.level})"
                ),
            ]
        )

    # ---------------------------------------------------------
    # ROUTE
    # ---------------------------------------------------------

    if route_model:

        message_lines.extend(
            [
                "",
                "Recommended Route:",
                (
                    f"- Route ID: "
                    f"{route_model.route_id}"
                ),
                (
                    f"- Distance: "
                    f"{route_model.distance_km:.2f} km"
                ),
                (
                    f"- Route Risk: "
                    f"{route_model.risk_score:.2f}"
                ),
                (
                    "- Status: "
                    f"{'SAFE' if route_model.safe else 'UNSAFE'}"
                ),
                (
                    f"- Waypoints: "
                    f"{len(route_model.waypoints)}"
                ),
            ]
        )

    # ---------------------------------------------------------
    # FINAL MESSAGE
    # ---------------------------------------------------------

    message = "\n".join(
        message_lines
    )

    # =========================================================
    # FINAL AGENT RESPONSE
    # =========================================================

    response = AgentResponse(
        message=message,
        map=map_model,
        pfz=pfz_data,
        risk=risk_model,
        route=route_model,
    )

    return {
        "response": response,
        "pending_action": None,
        "workflow_status": "COMPLETED",
    }