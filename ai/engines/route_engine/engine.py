import math

from .graph import (
    MarineGraph,
    create_route_grid,
    connect_grid,
    find_nearest_node,
    path_to_coordinates,
    apply_risk_constraints,
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

        Coordinates:
            (latitude, longitude)

        Returns:
            Distance in kilometres.
        """

        lat1, lon1 = point1
        lat2, lon2 = point2

        radius = 6371.0

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
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
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
        between the start location and PFZ.
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
    # BUILD RISK HELPER INPUT
    # =========================================================

    @staticmethod
    def build_risk_input(
        graph: MarineGraph,
        time: str,
    ) -> dict:
        """
        Convert graph nodes into the input format
        expected by the Risk Helper.

        The Risk Helper receives:

            {
                "nodes": [
                    {
                        "node_id": "...",
                        "latitude": ...,
                        "longitude": ...
                    }
                ],
                "time": "..."
            }
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
    # APPLY RISK CONSTRAINTS
    # =========================================================

    @staticmethod
    def apply_risk(
        graph: MarineGraph,
        time: str,
    ) -> MarineGraph:
        """
        Send every grid node to the Risk Helper.

        Unsafe nodes are removed from the graph.

        Restricted/protected areas are currently kept
        as False inside the Risk Helper and are not
        applied here yet.
        """

        risk_input = RouteEngine.build_risk_input(
            graph,
            time,
        )

        routing_risk = process_grid(
            risk_input
        )

        risk_lookup = {
            result["node_id"]: result
            for result in routing_risk
        }

        return apply_risk_constraints(
            graph,
            risk_lookup,
        )

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
        Find the graph nodes nearest to the
        requested start and PFZ destination.
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
        # RESULT
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
        max_routes: int = 3,
        rows: int = 10,
        columns: int = 10,
        time: str | None = None,
    ) -> CandidateRoutes:
        """
        Generate multiple candidate routes.

        Flow:

            1. Build geographic grid
            2. Connect grid nodes
            3. Send grid nodes to Risk Helper
            4. Remove unsafe nodes
            5. Find start/destination nodes
            6. Generate candidate paths
            7. Convert paths into RouteResults
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
        # 2. APPLY RISK ENGINE
        # -----------------------------------------------------
        #
        # The Risk Helper needs a timestamp.
        #
        # Until API integration is added, a timestamp
        # can be supplied directly through `time`.
        #

        if time is not None:

            graph = self.apply_risk(
                graph,
                time,
            )

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
    # PROCESS
    # =========================================================

    def process(
        self,
        request: RouteRequest,
        max_routes: int = 3,
        rows: int = 10,
        columns: int = 10,
        time: str | None = None,
    ) -> CandidateRoutes:
        """
        Main entry point for the Route Engine.
        """

        return self.generate_routes(
            request=request,
            max_routes=max_routes,
            rows=rows,
            columns=columns,
            time=time,
        )