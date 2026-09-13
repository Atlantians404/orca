from datetime import datetime


from .engine import RouteEngine
from .schemas import RouteRequest


def _build_route_request(state) -> RouteRequest:
    """
    Build a RouteRequest using:
    - user's current location as route start
    - selected PFZ as route destination
    - selected fishing time from time_context
    """

    location = state.get("location")
    selected_pfz = state.get("selected_pfz")

    if not location:
        raise ValueError(
            "User location is required to generate a route."
        )

    if not selected_pfz:
        raise ValueError(
            "A selected PFZ is required to generate a route."
        )

    start_latitude = location.latitude
    start_longitude = location.longitude

    destination_latitude = selected_pfz.get("latitude")
    destination_longitude = selected_pfz.get("longitude")

    if destination_latitude is None or destination_longitude is None:
        coordinates = selected_pfz.get("coordinates")

        if isinstance(coordinates, dict):
            destination_latitude = coordinates.get("latitude")
            destination_longitude = coordinates.get("longitude")

    if start_latitude is None or start_longitude is None:
        raise ValueError(
            "Start location coordinates are missing."
        )

    if destination_latitude is None or destination_longitude is None:
        raise ValueError(
            "Selected PFZ coordinates are missing."
        )

    coastal_reference = selected_pfz.get("coastal_reference")

    if not coastal_reference:
        coastal_reference = selected_pfz.get("name")

    if not coastal_reference:
        coastal_reference = selected_pfz.get("pfz_name")

    if not coastal_reference:
        coastal_reference = "Selected PFZ"

    time_context = state.get("time_context")

    if not time_context:
        raise ValueError(
            "Time is required for route generation."
        )

    slots = getattr(time_context, "slots", None)

    if not slots:
        raise ValueError(
            "Time is required for route generation."
        )

    fishing_time = slots[0].start_time

    if not fishing_time:
        raise ValueError(
            "Fishing start time is missing."
        )

    return RouteRequest(
        start={
            "latitude": start_latitude,
            "longitude": start_longitude,
        },
        destination={
            "latitude": destination_latitude,
            "longitude": destination_longitude,
            "coastal_reference": coastal_reference,
        },
        time=fishing_time,
    )


def _build_risk_nodes(route) -> list[dict]:
    risk_nodes = []

    for waypoint in route.waypoints:
        risk_nodes.append({
            "node_id": (
                waypoint.node_id
                or f"{waypoint.latitude}:{waypoint.longitude}"
            ),
            "latitude": waypoint.latitude,
            "longitude": waypoint.longitude,
        })

    return risk_nodes


async def _evaluate_route(route, state) -> dict:
    risk_nodes = _build_risk_nodes(route)

    if not risk_nodes:
        return {
            "route_id": route.route_id,
            "distance_km": route.distance_km,
            "risk_score": 100.0,
            "safe": False,
            "waypoints": [],
            "geojson": route.geojson,
            "nodes": [],
        }

    time_context = state.get("time_context")

    if not time_context:
        raise ValueError(
            "Time context is required for route risk evaluation."
        )

    slots = getattr(time_context, "slots", None)

    if not slots:
        raise ValueError(
            "No time slots available for route risk evaluation."
        )

    fishing_time = slots[0].start_time
    fishing_date = slots[0].date

    if not fishing_time:
        raise ValueError(
            "Fishing start time is missing."
        )

    if not fishing_date:
        raise ValueError(
            "Fishing date is missing."
        )

    # Convert ORCA date format:
    # "29 Aug 2026"
    #
    # into Open-Meteo compatible date:
    # "2026-08-29"
    try:
        weather_date = datetime.strptime(
            fishing_date,
            "%d %b %Y"
        ).strftime("%Y-%m-%d")
    except ValueError:
        # If the date is already ISO formatted,
        # keep it as-is.
        try:
            weather_date = datetime.strptime(
                fishing_date,
                "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Unsupported date format: {fishing_date}"
            )

    # Keep the original ORCA time for the Risk Engine
    # and Marine Batch.
    #
    # Send a full ISO datetime specifically for Weather Batch
    # because Open-Meteo requires a complete date + time.
    weather_time = (
        f"{weather_date}T{fishing_time}"
    )

    from ai.tools.risk_helper import process_grid

    risk_input = {
        "nodes": risk_nodes,
        "time": fishing_time,
        "weather_time": weather_time,
    }

    risk_results = await process_grid(
        risk_input
    )

    if not risk_results:
        return {
            "route_id": route.route_id,
            "distance_km": route.distance_km,
            "risk_score": 100.0,
            "safe": False,
            "waypoints": [
                {
                    "node_id": waypoint.node_id,
                    "latitude": waypoint.latitude,
                    "longitude": waypoint.longitude,
                }
                for waypoint in route.waypoints
            ],
            "geojson": route.geojson,
            "nodes": risk_nodes,
        }

    # Route risk = highest-risk waypoint
    route_risk_score = max(
        result.get("risk_score", 100.0)
        for result in risk_results
    )

    route_safe = all(
        result.get("safe", False)
        for result in risk_results
    )

    waypoints = [
        {
            "node_id": waypoint.node_id,
            "latitude": waypoint.latitude,
            "longitude": waypoint.longitude,
        }
        for waypoint in route.waypoints
    ]

    return {
        "route_id": route.route_id,
        "distance_km": route.distance_km,
        "risk_score": route_risk_score,
        "safe": route_safe,
        "waypoints": waypoints,
        "geojson": route.geojson,
        "nodes": [
            {
                **node,
                "risk_score": risk_result.get(
                    "risk_score"
                ),
                "safe": risk_result.get(
                    "safe"
                ),
            }
            for node, risk_result in zip(
                risk_nodes,
                risk_results,
            )
        ],
    }


def _select_safest_route(
    evaluated_routes: list[dict]
) -> dict | None:

    safe_routes = [
        route
        for route in evaluated_routes
        if route.get("safe", False)
    ]

    if not safe_routes:
        return None

    return min(
        safe_routes,
        key=lambda route: route.get(
            "risk_score",
            float("inf")
        ),
    )


async def route_node(state) -> dict:

    try:
        request = _build_route_request(state)

        engine = RouteEngine()

        candidate_routes = engine.generate_routes(
            request,
            max_routes=3,
        )

        if not candidate_routes.routes:
            return {
                "route_result": {
                    "candidate_routes": [],
                    "safe_route": None,
                },
                "workflow_status": "COMPLETED",
            }

        evaluated_routes = []

        for route in candidate_routes.routes:
            evaluation = await _evaluate_route(
                route,
                state,
            )

            evaluated_routes.append(
                evaluation
            )

        safe_route = _select_safest_route(
            evaluated_routes
        )

        formatted_candidate_routes = []

        for route in evaluated_routes:
            formatted_candidate_routes.append({
                "route_id": route.get("route_id"),
                "distance_km": route.get("distance_km"),
                "risk_score": route.get("risk_score"),
                "safe": route.get("safe"),
                "waypoints": route.get(
                    "waypoints",
                    []
                ),
                "geojson": route.get("geojson"),
                "nodes": route.get(
                    "nodes",
                    []
                ),
            })

        route_result = {
            "candidate_routes": formatted_candidate_routes,
            "safe_route": safe_route,
        }

        return {
            "route_result": route_result,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    except ValueError as exc:
        return {
            "route_result": {
                "candidate_routes": [],
                "safe_route": None,
                "error": str(exc),
            },
            "pending_action": None,
            "workflow_status": "COMPLETED",
        }

    except Exception as exc:
        return {
            "route_result": {
                "candidate_routes": [],
                "safe_route": None,
                "error": (
                    "Route generation failed: "
                    f"{str(exc)}"
                ),
            },
            "pending_action": None,
            "workflow_status": "COMPLETED",
        }