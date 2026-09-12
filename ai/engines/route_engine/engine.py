import math
from typing import Any

from .graph import (
    MarineGraph,
    create_route_grid,
    connect_grid,
    find_nearest_node,
    path_to_coordinates,
    apply_zone_constraints,
)

from .pathfinding import (
    generate_candidate_paths,
)

from .geometry import (
    create_linestring,
)

from .schemas import (
    RouteRequest,
    RouteResult,
    CandidateRoutes,
    Coordinate,
)

from .waypoints import (
    generate_waypoints,
)


class RouteEngine:

    # =========================================================
    # DISTANCE
    # =========================================================

    @staticmethod
    def calculate_distance(
        point1: tuple[float, float],
        point2: tuple[float, float],
    ) -> float:

        lat1, lon1 = point1
        lat2, lon2 = point2

        if not (
            -90 <= lat1 <= 90
            and -180 <= lon1 <= 180
        ):
            raise ValueError(
                "Invalid coordinates for point 1"
            )

        if not (
            -90 <= lat2 <= 90
            and -180 <= lon2 <= 180
        ):
            raise ValueError(
                "Invalid coordinates for point 2"
            )

        earth_radius_km = 6371.0

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)

        delta_lat = math.radians(
            lat2 - lat1
        )

        delta_lon = math.radians(
            lon2 - lon1
        )

        a = (
            math.sin(delta_lat / 2) ** 2
            +
            math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )

        return earth_radius_km * c

    # =========================================================
    # BUILD GRAPH
    # =========================================================

    @staticmethod
    def build_graph(
        start: Coordinate,
        destination: Coordinate,
        rows: int = 10,
        columns: int = 10,
    ) -> MarineGraph:

        graph = create_route_grid(
            start_latitude=start.latitude,
            start_longitude=start.longitude,
            goal_latitude=destination.latitude,
            goal_longitude=destination.longitude,
            rows=rows,
            columns=columns,
        )

        graph = connect_grid(
            graph,
            rows=rows,
            columns=columns,
        )

        return graph

    # =========================================================
    # FIND START / DESTINATION NODES
    # =========================================================

    @staticmethod
    def find_route_nodes(
        graph: MarineGraph,
        start: Coordinate,
        destination: Coordinate,
    ) -> tuple[str, str]:

        start_node = find_nearest_node(
            graph,
            start.latitude,
            start.longitude,
        )

        destination_node = find_nearest_node(
            graph,
            destination.latitude,
            destination.longitude,
        )

        return (
            start_node,
            destination_node,
        )

    # =========================================================
    # CREATE ROUTE RESULT
    # =========================================================

    @staticmethod
    def create_route_result(
        graph: MarineGraph,
        path: list[str],
        distance: float,
        start: Coordinate,
        destination: Coordinate,
        coastal_reference: str,
        route_number: int,
    ) -> RouteResult:

        coordinates = path_to_coordinates(
            graph,
            path,
        )

        waypoints = generate_waypoints(
            graph,
            path,
        )

        linestring = create_linestring(
            coordinates
        )

        geojson = {
            "type": "Feature",
            "properties": {
                "route_id": f"ROUTE_{route_number}",
                "coastal_reference": coastal_reference,
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        longitude,
                        latitude,
                    ]
                    for latitude, longitude
                    in coordinates
                ],
            },
        }

        return RouteResult(
            route_id=f"ROUTE_{route_number}",
            coastal_reference=coastal_reference,
            start=start,
            destination=destination,
            waypoints=waypoints,
            distance_km=distance,
            geojson=geojson,
        )

    # =========================================================
    # GENERATE CANDIDATE ROUTES
    # =========================================================

    def generate_routes(
        self,
        request: RouteRequest,
        time: str | None = None,
        max_routes: int = 3,
        rows: int = 10,
        columns: int = 10,
    ) -> CandidateRoutes:

        if max_routes < 1:
            raise ValueError(
                "max_routes must be at least 1"
            )

        if time is None:
            time = request.time

        if time is None:
            raise ValueError(
                "Time is required for route generation."
            )

        graph = self.build_graph(
            start=request.start,
            destination=request.destination,
            rows=rows,
            columns=columns,
        )

        # -----------------------------------------------------
        # HARD CONSTRAINT:
        # RESTRICTED ZONES
        # -----------------------------------------------------

        if (
            request.constraints.avoid_restricted_zones
            and request.constraints.restricted_zones
        ):

            graph = apply_zone_constraints(
                graph,
                request.constraints.restricted_zones,
            )

        start_node, destination_node = (
            self.find_route_nodes(
                graph,
                request.start,
                request.destination,
            )
        )

        candidates = generate_candidate_paths(
            graph,
            start_node,
            destination_node,
            max_routes=max_routes,
        )

        routes = []

        for index, (
            path,
            distance,
        ) in enumerate(
            candidates,
            start=1,
        ):

            route = self.create_route_result(
                graph=graph,
                path=path,
                distance=distance,
                start=request.start,
                destination=request.destination,
                coastal_reference=(
                    request.destination.coastal_reference
                ),
                route_number=index,
            )

            routes.append(route)

        if not routes:
            raise ValueError(
                "No candidate routes could be generated."
            )

        return CandidateRoutes(
            coastal_reference=(
                request.destination.coastal_reference
            ),
            routes=routes,
        )

    # =========================================================
    # BACKWARD COMPATIBILITY
    # =========================================================

    @staticmethod
    def find_route(
        request: RouteRequest | None = None,
        *,
        start_latitude: float | None = None,
        start_longitude: float | None = None,
        goal_latitude: float | None = None,
        goal_longitude: float | None = None,
        restricted_zones: list | None = None,
    ) -> RouteResult:

        if request is None:

            if (
                start_latitude is None
                or start_longitude is None
                or goal_latitude is None
                or goal_longitude is None
            ):
                raise ValueError(
                    "Start and destination coordinates are required."
                )

            from .schemas import (
                RouteDestination,
                RouteConstraints,
            )

            request = RouteRequest(
                start=Coordinate(
                    latitude=start_latitude,
                    longitude=start_longitude,
                ),
                destination=RouteDestination(
                    coastal_reference="UNKNOWN",
                    latitude=goal_latitude,
                    longitude=goal_longitude,
                ),
                constraints=RouteConstraints(
                    restricted_zones=(
                        restricted_zones or []
                    )
                ),
            )

        if request.time is None:
            request.time = "00:00"

        result = RouteEngine().generate_routes(
            request=request,
            time=request.time,
            max_routes=1,
        )

        return result.routes[0]

    @staticmethod
    def find_routes(
        request: RouteRequest,
        max_routes: int = 3,
    ) -> CandidateRoutes:

        if max_routes < 1:
            raise ValueError(
                "max_routes must be at least 1"
            )

        return RouteEngine().generate_routes(
            request=request,
            time=request.time,
            max_routes=max_routes,
        )

    # =========================================================
    # PROCESS
    # =========================================================

    def process(
        self,
        state: dict[str, Any],
        max_routes: int = 3,
        rows: int = 10,
        columns: int = 10,
    ) -> dict[str, Any]:

        location = state.get(
            "location"
        )

        selected_pfz = state.get(
            "selected_pfz"
        )

        time_context = state.get(
            "time_context"
        )

        if location is None:
            raise ValueError(
                "AgentState.location is required."
            )

        if selected_pfz is None:
            raise ValueError(
                "AgentState.selected_pfz is required."
            )

        if time_context is None:
            raise ValueError(
                "AgentState.time_context is required."
            )

        if hasattr(location, "latitude"):
            start_latitude = location.latitude
            start_longitude = location.longitude
        else:
            start_latitude = location["latitude"]
            start_longitude = location["longitude"]

        if hasattr(selected_pfz, "latitude"):
            destination_latitude = selected_pfz.latitude
            destination_longitude = selected_pfz.longitude
            coastal_reference = (
                selected_pfz.coastal_reference
            )
        else:
            destination_latitude = selected_pfz["latitude"]
            destination_longitude = selected_pfz["longitude"]
            coastal_reference = (
                selected_pfz.get(
                    "coastal_reference"
                )
                or selected_pfz.get("name")
                or "UNKNOWN"
            )

        if hasattr(time_context, "isoformat"):
            time_value = time_context.isoformat()
        elif isinstance(time_context, dict):
            time_value = (
                time_context.get("datetime")
                or time_context.get("time")
                or time_context.get("iso")
            )
        else:
            time_value = str(time_context)

        request = RouteRequest(
            start=Coordinate(
                latitude=start_latitude,
                longitude=start_longitude,
            ),
            destination={
                "coastal_reference": coastal_reference,
                "latitude": destination_latitude,
                "longitude": destination_longitude,
            },
            time=time_value,
        )

        result = self.generate_routes(
            request=request,
            time=time_value,
            max_routes=max_routes,
            rows=rows,
            columns=columns,
        )

        return {
            "route_result": result.model_dump(),
            "workflow_status": "route_candidates_generated",
        }