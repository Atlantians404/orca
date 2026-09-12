import asyncio
from typing import Any

from .engine import RouteEngine
from .schemas import (
    Coordinate,
    RouteConstraints,
    RouteDestination,
    RouteRequest,
    RestrictedZone,
)
from .zone_repository import get_route_zones

from ai.tools.risk_helper import process_grid


async def _build_route_request(
    state: dict[str, Any],
    restricted_zones: list[dict[str, Any]],
) -> RouteRequest:
    location = state.get("location")
    selected_pfz = state.get("selected_pfz")
    time_context = state.get("time_context")

    if not location:
        raise ValueError("Route node requires location")

    if not selected_pfz:
        raise ValueError("Route node requires selected_pfz")

    if not time_context:
        raise ValueError("Route node requires time_context")

    start = Coordinate(
        latitude=location["latitude"],
        longitude=location["longitude"],
    )

    destination = RouteDestination(
        coastal_reference=selected_pfz["coastal_reference"],
        latitude=selected_pfz["latitude"],
        longitude=selected_pfz["longitude"],
    )

    converted_zones = []

    for zone in restricted_zones:
        converted_zones.append(
            RestrictedZone(
                name=zone.get("name", "Unknown"),
                state=zone.get("state", ""),
                type=zone.get("type", "MARINE_RESTRICTED_AREA"),
                restriction_level=zone.get(
                    "restriction_level",
                    "RESTRICTED",
                ),
                latitude=zone["latitude"],
                longitude=zone["longitude"],
                geometry=zone.get("geometry"),
                id=zone.get("id"),
                coordinates=zone.get("coordinates"),
            )
        )

    return RouteRequest(
        start=start,
        destination=destination,
        time=time_context.get("specific_time")
        or time_context.get("time"),
        constraints=RouteConstraints(
            avoid_restricted_zones=True,
            restricted_zones=converted_zones,
        ),
    )


async def _build_risk_nodes(route: Any) -> list[dict[str, Any]]:
    nodes = []

    for waypoint in route.waypoints:
        nodes.append(
            {
                "node_id": waypoint.node_id
                or (
                    f"{waypoint.latitude}:"
                    f"{waypoint.longitude}"
                ),
                "latitude": waypoint.latitude,
                "longitude": waypoint.longitude,
            }
        )

    return nodes


async def _evaluate_route(
    route: Any,
    time: str,
) -> dict[str, Any]:
    nodes = await _build_risk_nodes(route)

    if not nodes:
        return {
            "route_id": route.route_id,
            "distance_km": route.distance_km,
            "risk_score": 100.0,
            "safe": False,
            "nodes": [],
        }

    risk_results = await process_grid(
        {
            "nodes": nodes,
            "time": time,
        }
    )

    if not risk_results:
        return {
            "route_id": route.route_id,
            "distance_km": route.distance_km,
            "risk_score": 100.0,
            "safe": False,
            "nodes": [],
        }

    route_risk_score = max(
        result["risk_score"]
        for result in risk_results
    )

    route_safe = all(
        result["safe"]
        for result in risk_results
    )

    return {
        "route_id": route.route_id,
        "distance_km": route.distance_km,
        "risk_score": route_risk_score,
        "safe": route_safe,
        "nodes": risk_results,
    }


async def _evaluate_routes(
    routes: list[Any],
    time: str,
) -> list[dict[str, Any]]:
    results = await asyncio.gather(
        *(
            _evaluate_route(route, time)
            for route in routes
        )
    )

    return list(results)


async def _select_safest_route(
    route_results: list[dict[str, Any]],
) -> dict[str, Any] | None:

    safe_routes = [
        route
        for route in route_results
        if route["safe"]
    ]

    if not safe_routes:
        return None

    return min(
        safe_routes,
        key=lambda route: (
            route["risk_score"],
            route["distance_km"],
        ),
    )


async def route_node(
    state: dict[str, Any],
) -> dict[str, Any]:

    # --------------------------------------------------
    # 1. Load real MongoDB marine zones
    # --------------------------------------------------

    zones = await get_route_zones()

    restricted_zones = zones.get(
        "restricted",
        [],
    )

    protected_zones = zones.get(
        "protected",
        [],
    )

    # --------------------------------------------------
    # 2. Build RouteRequest
    # --------------------------------------------------

    request = await _build_route_request(
        state,
        restricted_zones,
    )

    if not request.time:
        raise ValueError(
            "Route node requires a valid time"
        )

    # --------------------------------------------------
    # 3. Generate up to 3 candidate routes
    # --------------------------------------------------

    engine = RouteEngine()

    candidate_routes = engine.generate_routes(
        request,
        max_routes=3,
    )

    routes = candidate_routes.routes

    # --------------------------------------------------
    # 4. Evaluate all routes with Risk Helper
    # --------------------------------------------------

    route_risk_results = await _evaluate_routes(
        routes,
        request.time,
    )

    # --------------------------------------------------
    # 5. Select safest route
    # --------------------------------------------------

    safest_route = await _select_safest_route(
        route_risk_results
    )

    # --------------------------------------------------
    # 6. Prepare candidate route response
    # --------------------------------------------------

    candidate_route_data = []

    for route, risk in zip(
        routes,
        route_risk_results,
    ):
        candidate_route_data.append(
            {
                "route_id": route.route_id,
                "distance_km": route.distance_km,
                "risk_score": risk["risk_score"],
                "safe": risk["safe"],
                "waypoints": [
                    {
                        "node_id": waypoint.node_id,
                        "latitude": waypoint.latitude,
                        "longitude": waypoint.longitude,
                    }
                    for waypoint in route.waypoints
                ],
                "geojson": route.geojson,
            }
        )

    # --------------------------------------------------
    # 7. Build final route_result
    # --------------------------------------------------

    route_result = {
        "coastal_reference": (
            request.destination.coastal_reference
        ),
        "candidate_routes": candidate_route_data,
        "safe_route": safest_route,
        "zones": {
            "restricted": restricted_zones,
            "protected": protected_zones,
        },
    }

    # --------------------------------------------------
    # 8. Build risk_result
    # --------------------------------------------------

    risk_result = {
        "routes": route_risk_results,
        "selected_route_id": (
            safest_route["route_id"]
            if safest_route
            else None
        ),
        "safe_route_found": (
            safest_route is not None
        ),
    }

    # --------------------------------------------------
    # 9. Return AgentState updates
    # --------------------------------------------------

    return {
        "route_result": route_result,
        "risk_result": risk_result,
        "workflow_status": (
            "route_completed"
            if safest_route
            else "no_safe_route_found"
        ),
    }