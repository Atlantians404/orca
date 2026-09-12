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


def _get_value(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def _get_route_time(time_context: Any) -> str | None:
    if not time_context:
        return None

    specific_time = _get_value(time_context, "specific_time")

    if specific_time:
        return specific_time

    time_value = _get_value(time_context, "time")

    if time_value:
        return time_value

    slots = _get_value(time_context, "slots", [])

    if slots:
        first_slot = slots[0]

        date = _get_value(first_slot, "date")
        start_time = _get_value(first_slot, "start_time")

        if date and start_time:
            return f"{date}T{start_time}:00"

    return None


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

    latitude = _get_value(location, "latitude")
    longitude = _get_value(location, "longitude")

    if latitude is None or longitude is None:
        raise ValueError(
            "Route node requires valid location coordinates"
        )

    pfz_latitude = _get_value(selected_pfz, "latitude")
    pfz_longitude = _get_value(selected_pfz, "longitude")

    if pfz_latitude is None or pfz_longitude is None:
        raise ValueError(
            "Selected PFZ requires valid coordinates"
        )

    coastal_reference = _get_value(
        selected_pfz,
        "coastal_reference",
        _get_value(selected_pfz, "name", "Selected PFZ"),
    )

    start = Coordinate(
        latitude=latitude,
        longitude=longitude,
    )

    destination = RouteDestination(
        coastal_reference=coastal_reference,
        latitude=pfz_latitude,
        longitude=pfz_longitude,
    )

    converted_zones = []

    for zone in restricted_zones:
        converted_zones.append(
            RestrictedZone(
                name=zone.get("name", "Unknown"),
                state=zone.get("state", ""),
                type=zone.get(
                    "type",
                    "MARINE_RESTRICTED_AREA",
                ),
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

    route_time = _get_route_time(time_context)

    return RouteRequest(
        start=start,
        destination=destination,
        time=route_time,
        constraints=RouteConstraints(
            avoid_restricted_zones=True,
            restricted_zones=converted_zones,
        ),
    )


async def _build_risk_nodes(
    route: Any,
) -> list[dict[str, Any]]:

    nodes = []

    for waypoint in route.waypoints:
        nodes.append(
            {
                "node_id": (
                    waypoint.node_id
                    or (
                        f"{waypoint.latitude}:"
                        f"{waypoint.longitude}"
                    )
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

    return list(
        await asyncio.gather(
            *(
                _evaluate_route(route, time)
                for route in routes
            )
        )
    )


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

    zones = await get_route_zones()

    restricted_zones = zones.get(
        "restricted",
        [],
    )

    protected_zones = zones.get(
        "protected",
        [],
    )

    request = await _build_route_request(
        state,
        restricted_zones,
    )

    if not request.time:
        raise ValueError(
            "Route node requires a valid time"
        )

    engine = RouteEngine()

    candidate_routes = engine.generate_routes(
        request,
        max_routes=3,
    )

    routes = candidate_routes.routes

    if not routes:
        return {
            "route_result": {
                "coastal_reference": (
                    request.destination.coastal_reference
                ),
                "candidate_routes": [],
                "safe_route": None,
                "zones": {
                    "restricted": restricted_zones,
                    "protected": protected_zones,
                },
            },
            "risk_result": {
                "routes": [],
                "selected_route_id": None,
                "safe_route_found": False,
            },
            "workflow_status": "no_routes_found",
        }

    route_risk_results = await _evaluate_routes(
        routes,
        request.time,
    )

    safest_route = await _select_safest_route(
        route_risk_results
    )

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

    return {
        "route_result": route_result,
        "risk_result": risk_result,
        "workflow_status": (
            "route_completed"
            if safest_route
            else "no_safe_route_found"
        ),
    }