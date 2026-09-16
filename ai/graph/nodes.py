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

from datetime import datetime
from zoneinfo import ZoneInfo
import json

from ai.schemas.agent_response import (
    AgentResponse,
    PFZData,
    RiskData,
    WaypointData,
    RouteData,
    MapData,
)


DEFAULT_RADIUS_KM = 50.0
MAX_PFZ_CANDIDATES = 20


# ============================================================
# HITL / USER INTENT HELPERS
# ============================================================

CANCEL_COMMANDS = {
    "cancel",
    "cancelled",
    "canceled",
    "stop",
    "exit",
    "quit",
    "abort",
    "never mind",
    "nevermind",
    "forget it",
}


def is_obvious_cancel(value) -> bool:
    """
    Fast deterministic cancellation check.

    This avoids an LLM call for obvious commands such as:
    'cancel', 'stop', 'exit', etc.
    """

    if not isinstance(value, str):
        return False

    normalized = " ".join(
        value.strip().casefold().split()
    )

    return normalized in CANCEL_COMMANDS


async def is_user_cancel_request(value) -> bool:
    """
    Determine whether a HITL response is a cancellation request.

    First perform a cheap deterministic check.

    If it is not obvious, use the LLM to determine whether
    the user is trying to cancel the current workflow.

    Returns:
        True  -> user wants to cancel
        False -> user is providing an actual answer
    """

    if is_obvious_cancel(value):
        return True

    if not isinstance(value, str):
        return False

    value = value.strip()

    if not value:
        return False

    prompt = f"""
You are a cancellation intent classifier.

The user is currently responding to an interactive step
in a fishing trip planning workflow.

Determine whether the user's message means that they want
to cancel, stop, abandon, or discontinue the current workflow.

User message:
{value}

Return ONLY valid JSON:

{{
    "intent": "cancel"
}}

OR

{{
    "intent": "answer"
}}

Rules:

- "cancel", "stop", "exit", "quit" -> cancel
- "I don't want to continue" -> cancel
- "forget this trip" -> cancel
- "I changed my mind" -> cancel
- "let's stop planning" -> cancel
- A location such as "Chennai" -> answer
- A time such as "tomorrow morning" -> answer
- A PFZ name -> answer
"""

    try:
        response = await llm.ainvoke(prompt)

        content = response.content.strip()

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

        result = json.loads(content)

        return result.get("intent") == "cancel"

    except Exception:
        # If the classifier fails, do not accidentally cancel
        # the user's workflow.
        return False


async def get_hitl_response(
    payload: dict,
):
    """
    Create a LangGraph HITL interrupt and classify the
    resumed user input for cancellation.

    Returns:
        ("cancel", None)
        ("answer", user_value)
    """

    user_value = interrupt(payload)

    if await is_user_cancel_request(user_value):
        return "cancel", None

    return "answer", user_value


def cancelled_response(
    reason: str = "User cancelled the workflow.",
) -> dict:
    """
    Return a consistent cancelled workflow state.
    """

    return {
        "pending_action": None,
        "workflow_status": "CANCELLED",
        "cancellation_reason": reason,
    }


def failed_response(
    message: str,
) -> dict:
    """
    Return a consistent failed workflow state.
    """

    return {
        "pending_action": None,
        "workflow_status": "FAILED",
        "error_message": message,
    }


# ============================================================
# GENERAL
# ============================================================

async def general_node(
    state: AgentState,
) -> dict:

    try:

        conversation_summary = (
            state.get("conversation_summary")
            or ""
        )

        # -----------------------------------------------------
        # Build prompt with conversation memory
        # -----------------------------------------------------

        if conversation_summary:

            user_prompt = f"""
Previous conversation summary:

{conversation_summary}

Current user message:

{state["prompt"]}

Use the previous conversation summary when it is
relevant to the current message.

Do not invent information that is not present in
the summary or current message.

Answer the current user message directly.
"""

        else:

            user_prompt = state["prompt"]

        # -----------------------------------------------------
        # General Agent
        # -----------------------------------------------------

        result = await general_agent(
            [
                {
                    "role": "user",
                    "content": user_prompt,
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

    except Exception as exc:

        return failed_response(
            f"Unable to process the request: {exc}"
        )


# ============================================================
# SAFETY
# ============================================================

async def safety_node(
    state: AgentState,
) -> dict:

    return {
        "response": {
            "message": "This is a safety assessment request.",
        },
        "workflow_status": "COMPLETED",
    }


# ============================================================
# PLANNING
# ============================================================

async def planning_node(
    state: AgentState,
) -> dict:

    return {
        "response": {
            "message": "This is a fishing trip planning request.",
        },
        "workflow_status": "IN_PROGRESS",
    }


# ============================================================
# LOCATION
# ============================================================

async def location_node(
    state: AgentState,
) -> dict:
    """
    Resolve the user's location.

    Priority:

    1. Existing coordinates -> use them.
    2. Existing place name -> geocode it.
    3. Missing location -> HITL.
    4. Invalid HITL input -> retry.
    5. Cancellation -> CANCELLED.
    """

    location = state.get("location")

    # --------------------------------------------------------
    # Already have valid coordinates
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Already have a generic place
    # --------------------------------------------------------

    if location and location.place:

        try:

            coordinates = await get_coordinates(
                location.place
            )

            latitude = coordinates.get("latitude")
            longitude = coordinates.get("longitude")

            if latitude is not None and longitude is not None:

                resolved_location = Location(
                    place=location.place,
                    latitude=float(latitude),
                    longitude=float(longitude),
                )

                return {
                    "location": resolved_location,
                    "pending_action": None,
                    "workflow_status": "IN_PROGRESS",
                }

        except Exception:
            pass

    # --------------------------------------------------------
    # Location missing / unresolved
    # --------------------------------------------------------

    action, user_location = await get_hitl_response(
        {
            "action": "GET_LOCATION",
            "message": (
                "Please provide your current fishing location."
            ),
            "options": [
                "Enter place name",
                "Enter latitude and longitude",
            ],
        }
    )

    # --------------------------------------------------------
    # Cancellation
    # --------------------------------------------------------

    if action == "cancel":

        return cancelled_response(
            "User cancelled while providing the location."
        )

    # --------------------------------------------------------
    # Validate response
    # --------------------------------------------------------

    if not isinstance(user_location, dict):

        return {
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    try:

        location = Location(
            **user_location
        )

    except Exception:

        return {
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    # --------------------------------------------------------
    # Coordinates directly supplied
    # --------------------------------------------------------

    if (
        location.latitude is not None
        and location.longitude is not None
    ):

        return {
            "location": location,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # --------------------------------------------------------
    # Place name supplied
    # --------------------------------------------------------

    if location.place:

        try:

            coordinates = await get_coordinates(
                location.place
            )

            latitude = coordinates.get("latitude")
            longitude = coordinates.get("longitude")

            if latitude is not None and longitude is not None:

                resolved_location = Location(
                    place=location.place,
                    latitude=float(latitude),
                    longitude=float(longitude),
                )

                return {
                    "location": resolved_location,
                    "pending_action": None,
                    "workflow_status": "IN_PROGRESS",
                }

        except Exception:
            pass

    # --------------------------------------------------------
    # Could not resolve
    # --------------------------------------------------------

    return {
        "pending_action": "GET_LOCATION",
        "workflow_status": "WAITING_FOR_USER",
    }


# ============================================================
# TIME
# ============================================================

async def time_node(state: AgentState):

    time_context = state.get("time_context")

    if time_context and time_context.slots:
        return {
            "time_context": time_context,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    while True:

        action, user_time = await get_hitl_response(
            {
                "action": "GET_TIME",
                "message": "When would you like to go fishing?",
            }
        )

        if action == "cancel":
            return cancelled_response(
                "The fishing trip planning was cancelled."
            )

        if not isinstance(user_time, str):
            continue

        user_time = user_time.strip()

        if not user_time:
            continue

        try:

            prompt = TIME_PROMPT.format(
                current_date=datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).strftime("%Y-%m-%d"),
                time_input=user_time,
            )

            response = await llm.ainvoke(prompt)

            content = response.content.strip()

            if content.startswith("```"):
                content = content.replace("```json", "", 1)
                content = content.replace("```", "", 1)

            extracted = json.loads(content)

            print("\n========== TIME DEBUG ==========")
            print("User input :", user_time)
            print("LLM output :", extracted)

        except Exception as e:

            print("\n========== TIME ERROR ==========")
            print(type(e).__name__, ":", e)
            print("User input :", user_time)
            print("================================")

            continue

        time_type = extracted.get("time_type")

        # ----------------------------------------------------
        # SPECIFIC
        # ----------------------------------------------------

        if time_type == "specific":

            time = extracted.get("time")

            if not time:
                continue

            try:

                resolved_time = build_specific_time(
                    date_expression=extracted.get("date"),
                    time=time,
                )

            except Exception as e:

                print("Specific time error:", e)
                continue

            if not resolved_time or not resolved_time.slots:
                continue

            print("\n✅ TIME CONTEXT CREATED")
            print(resolved_time)

            return {
                "time_context": resolved_time,
                "pending_action": None,
                "workflow_status": "IN_PROGRESS",
            }

        # ----------------------------------------------------
        # GENERIC
        # ----------------------------------------------------

        if time_type == "generic":

            period = extracted.get("period")

            if not period:
                continue

            try:

                resolved_time = build_generic_time(
                    date_expression=extracted.get("date"),
                    period=period,
                )

            except Exception as e:

                print("Generic time error:", e)
                continue

            if not resolved_time or not resolved_time.slots:
                continue

            print("\n✅ TIME CONTEXT CREATED")
            print(resolved_time)

            return {
                "time_context": resolved_time,
                "pending_action": None,
                "workflow_status": "IN_PROGRESS",
            }

        # ----------------------------------------------------
        # MISSING
        # ----------------------------------------------------

        if time_type == "missing":

            print("\n⚠️ TIME WAS MISSING")
            continue

        print("\n⚠️ UNKNOWN TIME TYPE:", time_type)

# ============================================================
# PFZ
# ============================================================

async def pfz_node(
    state: AgentState,
) -> dict:

    selected_pfz_name = state.get(
        "selected_pfz_name"
    )

    # --------------------------------------------------------
    # Existing PFZ selection
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Candidates already available
    # --------------------------------------------------------

    pfz_candidates = state.get(
        "pfz_candidates"
    )

    if pfz_candidates:

        return {
            "pfz_candidates": pfz_candidates,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # --------------------------------------------------------
    # Location required
    # --------------------------------------------------------

    location = state.get(
        "location"
    )

    if not location:

        return {
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    distance_km = state.get(
        "distance_km"
    )

    if distance_km is None:
        distance_km = DEFAULT_RADIUS_KM

    # --------------------------------------------------------
    # Retrieve PFZ candidates
    # --------------------------------------------------------

    try:

        result = get_pfz_candidates(
            latitude=location.latitude,
            longitude=location.longitude,
            radius_km=distance_km,
            number_of_zones=MAX_PFZ_CANDIDATES,
        )

    except Exception as exc:

        return failed_response(
            f"Unable to retrieve PFZ candidates: {exc}"
        )

    candidates = result.get(
        "pfz_zones",
        {},
    )

    # --------------------------------------------------------
    # No candidates
    # --------------------------------------------------------

    if not candidates:

        return {
            "pfz_candidates": {},
            "workflow_status": "COMPLETED",
            "response": {
                "message": result.get(
                    "message",
                    "No suitable PFZ zones were found.",
                ),
            },
        }

    return {
        "pfz_candidates": candidates,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


# ============================================================
# DATA COLLECTION
# ============================================================

async def data_collection_node(
    state: AgentState,
) -> dict:

    try:

        pfz_candidates = state.get(
            "pfz_candidates",
            {},
        )

        if isinstance(
            pfz_candidates,
            dict,
        ):

            pfz_list = list(
                pfz_candidates.values()
            )

        elif isinstance(
            pfz_candidates,
            list,
        ):

            pfz_list = pfz_candidates

        else:

            pfz_list = []

        collection_state = {
            **state,
            "pfz_candidates": pfz_list,
        }

        updated_state = await data_collection_engine(
            collection_state
        )

        return {
            "agent_data": updated_state.get(
                "agent_data",
                {},
            ),
            "workflow_status": "IN_PROGRESS",
        }

    except Exception as exc:

        return failed_response(
            f"Unable to collect marine data: {exc}"
        )


# ============================================================
# RISK
# ============================================================

async def risk_node(
    state: AgentState,
) -> dict:

    try:

        result = await risk_engine_node(
            state
        )

        risk_result = result.get(
            "risk_result"
        )

        if not risk_result:

            return failed_response(
                "No risk assessment was returned."
            )

        return {
            "risk_result": risk_result,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    except Exception as exc:

        return failed_response(
            f"Unable to calculate route risk: {exc}"
        )


# ============================================================
# PFZ SELECTION
# ============================================================

async def pfz_selection_node(
    state: AgentState,
) -> dict:

    # --------------------------------------------------------
    # Already selected
    # --------------------------------------------------------

    selected_pfz = state.get(
        "selected_pfz"
    )

    if selected_pfz:

        print("\n========== PFZ ALREADY SELECTED ==========")
        print("selected_pfz:", selected_pfz)
        print("selected_pfz_name:", state.get("selected_pfz_name"))
        print("==========================================\n")

        return {
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # --------------------------------------------------------
    # Risk results
    # --------------------------------------------------------

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
                "message": (
                    "No risk results were available."
                ),
            },
        }

    # --------------------------------------------------------
    # Build options
    # --------------------------------------------------------

    pfz_options = []

    for result in ranked_results:

        pfz_name = result.get(
            "pfz_name"
        )

        if not pfz_name:
            continue

        times = result.get(
            "times",
            [],
        )

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
                "message": (
                    "No valid PFZ options were found."
                ),
            },
        }

    # --------------------------------------------------------
    # HITL
    # --------------------------------------------------------

    action, selected_name = await get_hitl_response(
        {
            "action": "SELECT_PFZ",
            "message": (
                "Select a PFZ based on the risk assessment."
            ),
            "options": pfz_options,
        }
    )

    # --------------------------------------------------------
    # Cancellation
    # --------------------------------------------------------

    if action == "cancel":

        return cancelled_response(
            "User cancelled while selecting a PFZ."
        )

    # --------------------------------------------------------
    # Validate selection
    # --------------------------------------------------------

    if not isinstance(
        selected_name,
        str,
    ):

        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    requested_name = selected_name.strip()

    if not requested_name:

        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    requested_name = requested_name.casefold()

    # --------------------------------------------------------
    # Find matching ranked PFZ
    # --------------------------------------------------------

    selected_result = None

    for result in ranked_results:

        pfz_name = result.get(
            "pfz_name",
            "",
        )

        if (
            pfz_name.strip().casefold()
            == requested_name
        ):

            selected_result = result
            break

    # --------------------------------------------------------
    # Invalid selection
    # --------------------------------------------------------

    if selected_result is None:

        print("\n========== INVALID PFZ SELECTION ==========")
        print("User selected:", selected_name)
        print("Available:", [
            r.get("pfz_name")
            for r in ranked_results
        ])
        print("===========================================\n")

        return {
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    # --------------------------------------------------------
    # Find full PFZ candidate
    # --------------------------------------------------------

    candidates = state.get(
        "pfz_candidates",
        {},
    )

    selected_pfz = None

    if isinstance(
        candidates,
        dict,
    ):

        for candidate in candidates.values():

            candidate_name = candidate.get(
                "name",
                "",
            )

            if (
                candidate_name.strip().casefold()
                == requested_name
            ):

                selected_pfz = candidate
                break

    actual_name = selected_result.get(
        "pfz_name"
    )

    # --------------------------------------------------------
    # FINAL SELECTION
    # --------------------------------------------------------

    final_selected_pfz = (
        selected_pfz
        or selected_result
    )

    print("\n")
    print("======= PFZ SELECTION DEBUG =======")
    print("User selected       :", selected_name)
    print("Actual PFZ name     :", actual_name)
    print("selected_pfz        :", selected_pfz)
    print("selected_result     :", selected_result)
    print("final_selected_pfz  :", final_selected_pfz)
    print("final type          :", type(final_selected_pfz))
    print("===================================")
    print("\n")

    return {
        "selected_pfz_name": actual_name,
        "selected_pfz": final_selected_pfz,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }


# ============================================================
# ROUTE
# ============================================================

async def route_node(state: AgentState) -> dict:
    try:
        selected_pfz = state.get("selected_pfz")
        selected_pfz_name = state.get("selected_pfz_name")
        location = state.get("location")
        time_context = state.get("time_context")

        # =========================================================
        # DEBUG
        # =========================================================
        print("\n")
        print("========== ROUTE DEBUG ==========")
        print("selected_pfz:", selected_pfz)
        print("selected_pfz_name:", selected_pfz_name)
        print("location:", location)
        print("time_context:", time_context)
        print("route_required:", state.get("route_required"))
        print("workflow_status:", state.get("workflow_status"))
        print("=================================")
        print("\n")

        # =========================================================
        # VALIDATION
        # =========================================================
        if not selected_pfz:
            print("❌ ROUTE ERROR: selected_pfz is None")

            return failed_response(
                "Cannot generate route because no PFZ was selected."
            )

        if not location:
            print("❌ ROUTE ERROR: location is None")

            return failed_response(
                "Cannot generate route because no location was provided."
            )

        if not time_context:
            print("❌ ROUTE ERROR: time_context is None")

            return failed_response(
                "Cannot generate route because no time information was provided."
            )

        # =========================================================
        # ROUTE ENGINE
        # =========================================================
        print("✅ selected_pfz exists")
        print("✅ location exists")
        print("✅ time_context exists")
        print("➡️ Calling route_engine_node()")

        result = await route_engine_node(state)

        print("➡️ route_engine_node result:", result)

        return {
            "route_result": result,
            "workflow_status": "COMPLETED",
        }

    except Exception as e:
        print("\n❌ ROUTE NODE EXCEPTION:", repr(e))
        print("\n")

        return failed_response(
            f"Route generation failed: {str(e)}"
        )


# ============================================================
# FINAL RESPONSE
# ============================================================

async def final_response_node(state: AgentState):

    workflow_status = state.get("workflow_status")

    # ============================================================
    # CANCELLED
    # ============================================================

    if workflow_status == "CANCELLED":

        return {
            "response": AgentResponse(
                message=(
                    state.get("cancellation_reason")
                    or "The fishing trip planning was cancelled."
                )
            )
        }

    # ============================================================
    # FAILED
    # ============================================================

    if workflow_status == "FAILED":

        return {
            "response": AgentResponse(
                message=(
                    state.get("error_message")
                    or "Unable to complete the fishing trip planning."
                )
            )
        }

    # ============================================================
    # GET STATE DATA
    # ============================================================

    selected_pfz = state.get("selected_pfz")
    selected_pfz_name = state.get("selected_pfz_name")

    risk_result = state.get("risk_result") or {}

    route_result = state.get("route_result") or {}

    # ============================================================
    # PFZ DATA
    # ============================================================

    pfz_data = None

    if selected_pfz:

        pfz_data = PFZData(
            name=selected_pfz.get(
                "name",
                selected_pfz_name or "",
            ),
            latitude=selected_pfz.get(
                "latitude",
                0.0,
            ),
            longitude=selected_pfz.get(
                "longitude",
                0.0,
            ),
            distance_from_source_km=selected_pfz.get(
                "distance_from_source_km"
            ),
        )

    # ============================================================
    # RISK DATA
    # ============================================================

    risk_data = None

    ranked_results = risk_result.get(
        "ranked_results",
        []
    )

    if selected_pfz_name and ranked_results:

        selected_risk = None

        for result in ranked_results:

            if (
                result.get("pfz_name", "").lower()
                == selected_pfz_name.lower()
            ):
                selected_risk = result
                break

        if selected_risk:

            times = selected_risk.get(
                "times",
                []
            )

            if times:

                selected_time = times[0]

                risk_data = RiskData(
                    score=float(
                        selected_time.get(
                            "risk_score",
                            0.0,
                        )
                    ),
                    level=selected_time.get(
                        "risk_level",
                        "UNKNOWN",
                    ),
                )

    # ============================================================
    # ROUTE DATA
    # ============================================================

    route_data = None

    safe_route = route_result.get(
        "safe_route"
    )

    if safe_route:

        waypoints = []

        for waypoint in safe_route.get(
            "nodes",
            []
        ):

            waypoints.append(
                WaypointData(
                    latitude=float(
                        waypoint.get(
                            "latitude",
                            0.0,
                        )
                    ),
                    longitude=float(
                        waypoint.get(
                            "longitude",
                            0.0,
                        )
                    ),
                    risk_score=(
                        float(
                            waypoint["risk_score"]
                        )
                        if waypoint.get("risk_score")
                        is not None
                        else None
                    ),
                    safe=waypoint.get(
                        "safe"
                    ),
                )
            )

        route_data = RouteData(
            route_id=safe_route.get(
                "route_id",
                "",
            ),
            distance_km=float(
                safe_route.get(
                    "distance_km",
                    0.0,
                )
            ),
            risk_score=float(
                safe_route.get(
                    "risk_score",
                    0.0,
                )
            ),
            safe=bool(
                safe_route.get(
                    "safe",
                    False,
                )
            ),
            waypoints=waypoints,
            geojson=safe_route.get(
                "geojson"
            ),
        )

    # ============================================================
    # MAP DATA
    # ============================================================

    map_data = None

    if safe_route:

        geojson = safe_route.get(
            "geojson"
        )

        if geojson:

            geometry = geojson.get(
                "geometry",
                {}
            )

            coordinates = geometry.get(
                "coordinates",
                []
            )

            if coordinates:

                map_data = MapData(
                    coordinates=coordinates
                )

    # ============================================================
    # HUMAN READABLE MESSAGE
    # ============================================================

    if selected_pfz_name:

        message_parts = [
            f"Fishing trip planned successfully.",
            "",
            f"Selected PFZ: {selected_pfz_name}",
        ]

        if risk_data:

            message_parts.extend(
                [
                    "",
                    "Risk Assessment:",
                    (
                        f"- Score: {risk_data.score:.2f}"
                        f" ({risk_data.level})"
                    ),
                ]
            )

        if route_data:

            message_parts.extend(
                [
                    "",
                    "Recommended Route:",
                    f"- Route ID: {route_data.route_id}",
                    (
                        f"- Distance: "
                        f"{route_data.distance_km:.2f} km"
                    ),
                    (
                        f"- Route Risk: "
                        f"{route_data.risk_score:.2f}"
                    ),
                    (
                        f"- Status: "
                        f"{'SAFE' if route_data.safe else 'UNSAFE'}"
                    ),
                ]
            )

        message = "\n".join(
            message_parts
        )

    else:

        message = (
            "Fishing trip planning completed."
        )

    # ============================================================
    # BUILD STRUCTURED RESPONSE
    # ============================================================

    response = AgentResponse(
        message=message,
        map=map_data,
        pfz=pfz_data,
        risk=risk_data,
        route=route_data,
    )

    # ============================================================
    # RETURN
    # ============================================================

    return {
        "response": response,
        "workflow_status": "COMPLETED",
        "pending_action": None,
    }