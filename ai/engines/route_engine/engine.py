import math
from typing import Any

from .graph import (
    MarineGraph,
    create_route_grid,
    connect_grid,
    find_nearest_node,
    path_to_coordinates,
)

from .pathfinding import generate_candidate_paths

from .geometry import (
    create_linestring,
    linestring_to_geojson,
)

from .schemas import (
    RouteRequest,
    RouteResult,
    CandidateRoutes,
    Coordinate,
    Waypoint,
)

from ai.tools.risk_helper import process_grid


class RouteEngine:

    # =========================================================
    # HAVERSINE DISTANCE
    # =========================================================

    @staticmethod
    def calculate_distance(
        point1: tuple[float, float],
        point2: tuple[float, float],
    ) -> float:
        """
        Calculate Haversine distance between two
        geographic coordinates.

        Returns:
            Distance in kilometres.
        """

        lat1, lon1 = point1
        lat2, lon2 = point2

        radius = 6371.0

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)

        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )

        return radius * c

    # =========================================================
    # BUILD ROUTE GRID
    # =========================================================

    @staticmethod
    def build_graph(
        start: Coordinate,
        destination: Coordinate,
        rows: int = 10,
        columns: int = 10,
    ) -> MarineGraph:
        """
        Create and connect a geographic grid
        between the user's location and the selected PFZ.
        """

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
    # FIND ROUTE NODES
    # =========================================================

    @staticmethod
    def find_route_nodes(
        graph: MarineGraph,
        start: Coordinate,
        destination: Coordinate,
    ) -> tuple[str, str]:
        """
        Find the grid nodes nearest to the user's
        starting location and selected PFZ.
        """

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

        return start_node, destination_node

    # =========================================================
    # BUILD RISK HELPER INPUT
    # =========================================================

    @staticmethod
    def build_risk_input(
        graph: MarineGraph,
        time: str,
    ) -> dict[str, Any]:
        """
        Convert the generated route grid into the
        input format expected by risk_helper.process_grid().

        Restricted/protected areas are currently kept
        as False and will be integrated later.
        """

        nodes = []

        for node_id, node in graph.nodes.items():

            nodes.append(
                {
                    "node_id": node_id,
                    "latitude": node.latitude,
                    "longitude": node.longitude,
                }
            )

        return {
            "nodes": nodes,
            "time": time,
        }

    # =========================================================
    # EVALUATE GRID RISK
    # =========================================================

    @staticmethod
    def evaluate_grid_risk(
        graph: MarineGraph,
        time: str,
    ) -> list[dict[str, Any]]:
        """
        Send all generated grid nodes to the Risk Helper.

        Risk Helper collects the weather/marine data for
        each node and returns the corresponding risk score.
        """

        risk_input = RouteEngine.build_risk_input(
            graph=graph,
            time=time,
        )

        return process_grid(
            risk_input
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
        """
        Convert a graph path into a RouteResult.
        """

        coordinates = path_to_coordinates(
            graph,
            path,
        )

        # -----------------------------------------------------
        # WAYPOINTS
        # -----------------------------------------------------

        waypoints = [
            Waypoint(
                latitude=latitude,
                longitude=longitude,
            )
            for latitude, longitude in coordinates
        ]

        # -----------------------------------------------------
        # GEOJSON
        # -----------------------------------------------------

        linestring = create_linestring(
            coordinates
        )

        geojson = linestring_to_geojson(
            linestring
        )

        # -----------------------------------------------------
        # ROUTE RESULT
        # -----------------------------------------------------

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
    # GENERATE ROUTES
    # =========================================================

    def generate_routes(
        self,
        request: RouteRequest,
        time: str,
        max_routes: int = 3,
        rows: int = 10,
        columns: int = 10,
    ) -> CandidateRoutes:
        """
        Generate candidate routes between the user's
        location and the selected PFZ.

        The generated grid is also sent to the Risk Helper
        for node-level risk evaluation.
        """

        # -----------------------------------------------------
        # 1. BUILD GRID
        # -----------------------------------------------------

        graph = self.build_graph(
            start=request.start,
            destination=request.destination,
            rows=rows,
            columns=columns,
        )

        # -----------------------------------------------------
        # 2. EVALUATE GRID RISK
        # -----------------------------------------------------

        risk_results = self.evaluate_grid_risk(
            graph=graph,
            time=time,
        )

        # -----------------------------------------------------
        # NOTE:
        #
        # Risk results are currently collected but are not
        # modifying the graph/pathfinding weights yet.
        #
        # Next stage:
        # risk score → graph cost → risk-aware A*
        # -----------------------------------------------------

        _ = risk_results

        # -----------------------------------------------------
        # 3. FIND START AND DESTINATION NODES
        # -----------------------------------------------------

        start_node, destination_node = (
            self.find_route_nodes(
                graph,
                request.start,
                request.destination,
            )
        )

        # -----------------------------------------------------
        # 4. GENERATE CANDIDATE PATHS
        # -----------------------------------------------------

        candidates = generate_candidate_paths(
            graph,
            start_node,
            destination_node,
            max_routes=max_routes,
        )

        # -----------------------------------------------------
        # 5. CONVERT PATHS TO ROUTE RESULTS
        # -----------------------------------------------------

        routes = []

        for index, (path, distance) in enumerate(
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

        # -----------------------------------------------------
        # 6. RETURN CANDIDATE ROUTES
        # -----------------------------------------------------

        return CandidateRoutes(
            coastal_reference=(
                request.destination.coastal_reference
            ),
            routes=routes,
        )

    # =========================================================
    # PROCESS FROM AGENT STATE
    # =========================================================

    def process(
        self,
        state: dict[str, Any],
        max_routes: int = 3,
        rows: int = 10,
        columns: int = 10,
    ) -> dict[str, Any]:
        """
        Main Route Engine entry point.

        Reads:

            state["location"]
            state["selected_pfz"]
            state["time_context"]

        and generates candidate routes.

        The generated route result is stored in:

            state["route_result"]
        """

        # -----------------------------------------------------
        # 1. GET USER LOCATION
        # -----------------------------------------------------

        location = state.get("location")

        if location is None:
            raise ValueError(
                "Route Engine requires a location"
            )

        # -----------------------------------------------------
        # 2. GET SELECTED PFZ
        # -----------------------------------------------------

        selected_pfz = state.get("selected_pfz")

        if selected_pfz is None:
            raise ValueError(
                "Route Engine requires a selected PFZ"
            )

        # -----------------------------------------------------
        # 3. GET TIME CONTEXT
        # -----------------------------------------------------

        time_context = state.get("time_context")

        if (
            time_context is None
            or not time_context.slots
        ):
            raise ValueError(
                "Route Engine requires a time context"
            )

        # -----------------------------------------------------
        # 4. GET REQUESTED TIME
        # -----------------------------------------------------

        slot = time_context.slots[0]

        requested_time = slot.date

        if slot.start_time:
            requested_time += (
                f"T{slot.start_time}:00"
            )

        # -----------------------------------------------------
        # 5. CONVERT LOCATION TO ROUTE COORDINATE
        # -----------------------------------------------------

        start = Coordinate(
            latitude=location.latitude,
            longitude=location.longitude,
        )

        # -----------------------------------------------------
        # 6. CONVERT PFZ TO ROUTE DESTINATION
        # -----------------------------------------------------

        destination = {
            "coastal_reference": (
                selected_pfz["coastal_reference"]
            ),
            "latitude": selected_pfz["latitude"],
            "longitude": selected_pfz["longitude"],
        }

        request = RouteRequest(
            start=start,
            destination=destination,
        )

        # -----------------------------------------------------
        # 7. GENERATE ROUTES
        # -----------------------------------------------------

        result = self.generate_routes(
            request=request,
            time=requested_time,
            max_routes=max_routes,
            rows=rows,
            columns=columns,
        )

        # -----------------------------------------------------
        # 8. UPDATE AGENT STATE
        # -----------------------------------------------------

        return {
            **state,
            "route_result": result.model_dump(),
        }