from typing import Any

from ai.agent_state import AgentState

from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import (
    Coordinate,
    RouteDestination,
    RouteRequest,
)


async def route_engine_node(state: AgentState) -> dict[str, Any]:

    location = state.get("location")
    selected_pfz_id = state.get("selected_pfz_id")
    selected_pfz = state.get("selected_pfz")
    time_context = state.get("time_context")

    # ---------------------------------------------------------
    # 1. Location is required
    # ---------------------------------------------------------

    if location is None:
        return {
            "route_result": None,
            "pending_action": "GET_LOCATION",
            "workflow_status": "WAITING_FOR_USER",
        }

    # ---------------------------------------------------------
    # 2. Selected PFZ is required
    # ---------------------------------------------------------

    if selected_pfz is None:
        return {
            "route_result": None,
            "pending_action": "SELECT_PFZ",
            "workflow_status": "WAITING_FOR_USER",
        }

    # ---------------------------------------------------------
    # 3. Time context is required
    # ---------------------------------------------------------

    if time_context is None or not time_context.slots:
        return {
            "route_result": None,
            "pending_action": "GET_TIME",
            "workflow_status": "WAITING_FOR_USER",
        }

    # ---------------------------------------------------------
    # 4. Build START from AgentState.location
    # ---------------------------------------------------------

    start = Coordinate(
        latitude=location.latitude,
        longitude=location.longitude,
    )

    # ---------------------------------------------------------
    # 5. Build DESTINATION from selected PFZ
    # ---------------------------------------------------------

    destination = RouteDestination(
        coastal_reference=selected_pfz.get(
            "coastal_reference",
            selected_pfz_id or "SELECTED_PFZ",
        ),
        latitude=selected_pfz["latitude"],
        longitude=selected_pfz["longitude"],
    )

    # ---------------------------------------------------------
    # 6. Get route time from TimeContext
    # ---------------------------------------------------------

    slot = time_context.slots[0]

    requested_time = slot.date

    if slot.start_time:
        requested_time = (
            f"{requested_time}T{slot.start_time}:00"
        )

    # ---------------------------------------------------------
    # 7. Create RouteRequest
    # ---------------------------------------------------------

    request = RouteRequest(
        start=start,
        destination=destination,
    )

    # ---------------------------------------------------------
    # 8. Run Route Engine
    # ---------------------------------------------------------

    engine = RouteEngine()

    result = engine.generate_routes(
        request=request,
        time=requested_time,
        max_routes=3,
        rows=10,
        columns=10,
    )

    # ---------------------------------------------------------
    # 9. Convert Pydantic result to dictionary
    # ---------------------------------------------------------

    if hasattr(result, "model_dump"):
        result = result.model_dump()

    # ---------------------------------------------------------
    # 10. Update AgentState
    # ---------------------------------------------------------

    return {
        "route_result": result,
        "pending_action": None,
        "workflow_status": "IN_PROGRESS",
    }