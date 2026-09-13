from typing import Any

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

    # ---------------------------------------------------------
    # Start coordinates
    # ---------------------------------------------------------

    start_latitude = location.latitude
    start_longitude = location.longitude

    # ---------------------------------------------------------
    # Destination coordinates
    # ---------------------------------------------------------

    destination_latitude = selected_pfz.get("latitude")
    destination_longitude = selected_pfz.get("longitude")

    # Fallback: coordinates object
    if (
        destination_latitude is None
        or destination_longitude is None
    ):
        coordinates = selected_pfz.get("coordinates")

        if isinstance(coordinates, dict):
            destination_latitude = coordinates.get(
                "latitude"
            )
            destination_longitude = coordinates.get(
                "longitude"
            )

    # ---------------------------------------------------------
    # Validate coordinates
    # ---------------------------------------------------------

    if (
        start_latitude is None
        or start_longitude is None
    ):
        raise ValueError(
            "Start location coordinates are missing."
        )

    if (
        destination_latitude is None
        or destination_longitude is None
    ):
        raise ValueError(
            "Selected PFZ coordinates are missing."
        )

    # ---------------------------------------------------------
    # Coastal reference
    # ---------------------------------------------------------

    coastal_reference = selected_pfz.get(
        "coastal_reference"
    )

    if not coastal_reference:
        coastal_reference = selected_pfz.get("name")

    if not coastal_reference:
        coastal_reference = selected_pfz.get("pfz_name")

    if not coastal_reference:
        coastal_reference = "Selected PFZ"

    # ---------------------------------------------------------
    # Fishing time
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Build RouteRequest
    # ---------------------------------------------------------

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
    """
    Convert route waypoints into nodes that can be
    evaluated by the risk engine.
    """

    risk_nodes = []

    for waypoint in route.waypoints:

        risk_nodes.append(
            {
                "node_id": (
                    waypoint.node_id
                    or f"{waypoint.latitude}:{waypoint.longitude}"
                ),
                "latitude": waypoint.latitude,
                "longitude": waypoint.longitude,
            }
        )

    return risk_nodes


async def _evaluate_route(
    route,
    state,
) -> dict:
    """
    Evaluate risk at every waypoint in a route.

    Route risk is the maximum risk encountered
    anywhere along the route.
    """

    risk_nodes = _build_risk_nodes(route)

    # ---------------------------------------------------------
    # No waypoints
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Get fishing time
    # ---------------------------------------------------------

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

    if not fishing_time:
        raise ValueError(
            "Fishing start time is missing."
        )

    # ---------------------------------------------------------
    # Import here to avoid circular imports
    # ---------------------------------------------------------

    from ai.tools.risk_helper import process_grid

    # ---------------------------------------------------------
    # Build input expected by process_grid()
    # ---------------------------------------------------------

    risk_input = {
        "nodes": risk_nodes,
        "time": fishing_time,
    }

    # process_grid() is async
    risk_results = await process_grid(
        risk_input
    )

    # ---------------------------------------------------------
    # Risk engine returned nothing
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Overall route risk
    # ---------------------------------------------------------

    route_risk_score = max(
        result.get(
            "risk_score",
            100.0,
        )
        for result in risk_results
    )

    # Route is safe only when every waypoint is safe.
    route_safe = all(
        result.get(
            "safe",
            False,
        )
        for result in risk_results
    )

    # ---------------------------------------------------------
    # Preserve original waypoint coordinates
    # ---------------------------------------------------------

    waypoints = [
        {
            "node_id": waypoint.node_id,
            "latitude": waypoint.latitude,
            "longitude": waypoint.longitude,
        }
        for waypoint in route.waypoints
    ]

    # ---------------------------------------------------------
    # Build evaluated route
    # ---------------------------------------------------------

    return {
        "route_id": route.route_id,
        "distance_km": route.distance_km,
        "risk_score": route_risk_score,
        "safe": route_safe,

        # Intermediate route points
        "waypoints": waypoints,

        # Ready for frontend map rendering
        "geojson": route.geojson,

        # Risk information for every waypoint
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
    evaluated_routes: list[dict],
) -> dict | None:
    """
    Select the safest route.

    Only routes marked safe are considered.

    If multiple safe routes exist, the route with
    the lowest maximum risk score is selected.
    """

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
            float("inf"),
        ),
    )


async def route_node(state) -> dict:
    """
    Generate and evaluate candidate routes.

    The result contains:

    - candidate_routes
    - safe_route
    - waypoints
    - GeoJSON
    - route risk
    """

    try:

        # ---------------------------------------------------------
        # Build route request
        # ---------------------------------------------------------

        request = _build_route_request(
            state
        )

        # ---------------------------------------------------------
        # Create route engine
        # ---------------------------------------------------------

        engine = RouteEngine()

        # ---------------------------------------------------------
        # Generate candidate routes
        # ---------------------------------------------------------

        candidate_routes = engine.generate_routes(
            request,
            max_routes=3,
        )

        # ---------------------------------------------------------
        # No routes generated
        # ---------------------------------------------------------

        if not candidate_routes.routes:
            return {
                "route_result": {
                    "candidate_routes": [],
                    "safe_route": None,
                },
                "workflow_status": "COMPLETED",
            }

        # ---------------------------------------------------------
        # Evaluate every candidate route
        # ---------------------------------------------------------

        evaluated_routes = []

        for route in candidate_routes.routes:

            evaluation = await _evaluate_route(
                route,
                state,
            )

            evaluated_routes.append(
                evaluation
            )

        # ---------------------------------------------------------
        # Select safest route
        # ---------------------------------------------------------

        safe_route = _select_safest_route(
            evaluated_routes
        )

        # ---------------------------------------------------------
        # Build candidate route response
        # ---------------------------------------------------------

        formatted_candidate_routes = []

        for route in evaluated_routes:

            formatted_candidate_routes.append(
                {
                    "route_id": route.get(
                        "route_id"
                    ),

                    "distance_km": route.get(
                        "distance_km"
                    ),

                    "risk_score": route.get(
                        "risk_score"
                    ),

                    "safe": route.get(
                        "safe"
                    ),

                    # Waypoints for frontend
                    "waypoints": route.get(
                        "waypoints",
                        [],
                    ),

                    # GeoJSON LineString
                    "geojson": route.get(
                        "geojson"
                    ),

                    # Risk at each waypoint
                    "nodes": route.get(
                        "nodes",
                        [],
                    ),
                }
            )

        # ---------------------------------------------------------
        # Final route result
        # ---------------------------------------------------------

        route_result = {
            "candidate_routes": formatted_candidate_routes,
            "safe_route": safe_route,
        }

        return {
            "route_result": route_result,
            "pending_action": None,
            "workflow_status": "IN_PROGRESS",
        }

    # ---------------------------------------------------------
    # Expected route/request errors
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Unexpected errors
    # ---------------------------------------------------------

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