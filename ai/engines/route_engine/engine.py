import math
from typing import Any

from .graph import (
    MarineGraph,
    create_route_grid,
    connect_grid,
    find_nearest_node,
    path_to_coordinates,
)

from .pathfinding import (
    generate_candidate_paths,
    astar_with_risk,
)

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
        between the user's location and selected PFZ.
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
        Convert the route grid into the input format
        expected by risk_helper.process_grid().

        Restricted/protected areas remain False for now.
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
        Send every grid node to the Risk Helper.

        Returns results such as:

            [
                {
                    "node_id": "N1",
                    "risk_score": 25,
                    "safe": True
                },
                ...
            ]
        """

        risk_input = RouteEngine.build_risk_input(
            graph=graph,
            time=time,
        )

        return process_grid(risk_input)

    # =========================================================
    # CONVERT RISK RESULTS
    # =========================================================

    @staticmethod
    def build_risk_score_map(
        risk_results: list[dict[str, Any]],
    ) -> dict[str, float]:
        """
        Convert Risk Helper output into:

            {
                "N1": 25.0,
                "N2": 60.0,
                "N3": 82.0
            }

        This format is consumed by risk-aware A*.
        """

        risk_scores = {}

        for result in risk_results:

            node_id = result.get("node_id")
            risk_score = result.get("risk_score")

            if node_id is None:
                continue

            if risk_score is None:
                continue

            risk_scores[node_id] = float(
                risk_score
            )

        return risk_scores

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
    destination=Coordinate(
        latitude=destination.latitude,
        longitude=destination.longitude,
    ),
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
        location and selected PFZ.

        Risk Helper is used to evaluate every grid node.
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
        # 2. FIND START AND DESTINATION NODES
        # -----------------------------------------------------

        start_node, destination_node = (
            self.find_route_nodes(
                graph,
                request.start,
                request.destination,
            )
        )

        # -----------------------------------------------------
        # 3. EVALUATE GRID RISK
        # -----------------------------------------------------

        risk_results = self.evaluate_grid_risk(
            graph=graph,
            time=time,
        )

        # -----------------------------------------------------
        # 4. BUILD RISK SCORE MAP
        # -----------------------------------------------------

        risk_scores = self.build_risk_score_map(
            risk_results
        )

        # -----------------------------------------------------
        # 5. GENERATE RISK-AWARE PRIMARY ROUTE
        # -----------------------------------------------------

        risk_route, risk_cost = astar_with_risk(
            graph=graph,
            start=start_node,
            goal=destination_node,
            risk_scores=risk_scores,
            risk_weight=1.0,
        )

        # -----------------------------------------------------
        # 6. GENERATE NORMAL CANDIDATE ROUTES
        # -----------------------------------------------------

        candidates = generate_candidate_paths(
            graph,
            start_node,
            destination_node,
            max_routes=max_routes,
        )

        # -----------------------------------------------------
        # 7. PUT RISK-AWARE ROUTE FIRST
        # -----------------------------------------------------

        candidate_paths = [
            (risk_route, risk_cost)
        ]

        seen_paths = {
            tuple(risk_route)
        }

        for path, distance in candidates:

            path_key = tuple(path)

            if path_key not in seen_paths:

                candidate_paths.append(
                    (
                        path,
                        distance
                    )
                )

                seen_paths.add(
                    path_key
                )

        # Limit number of routes
        candidate_paths = candidate_paths[:max_routes]

        # -----------------------------------------------------
        # 8. CALCULATE PHYSICAL DISTANCE
        # -----------------------------------------------------

        routes = []

        for index, (path, _) in enumerate(
            candidate_paths,
            start=1,
        ):

            physical_distance = 0.0

            for source, target in zip(
                path,
                path[1:]
            ):

                edge = next(
                    (
                        edge
                        for edge
                        in graph.get_neighbors(source)
                        if edge.target == target
                    ),
                    None
                )

                if edge is None:
                    raise ValueError(
                        f"No edge between {source} and {target}"
                    )

                physical_distance += edge.weight

            route = self.create_route_result(
                graph=graph,
                path=path,
                distance=physical_distance,
                start=request.start,
                destination=request.destination,
                coastal_reference=(
                    request.destination.coastal_reference
                ),
                route_number=index,
            )

            routes.append(route)

        # -----------------------------------------------------
        # 9. RETURN CANDIDATE ROUTES
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

        Generates routes and stores the result in:

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

        selected_pfz = state.get(
            "selected_pfz"
        )

        if selected_pfz is None:
            raise ValueError(
                "Route Engine requires a selected PFZ"
            )

        # -----------------------------------------------------
        # 3. GET TIME CONTEXT
        # -----------------------------------------------------

        time_context = state.get(
            "time_context"
        )

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
        # 5. CREATE START COORDINATE
        # -----------------------------------------------------

        start = Coordinate(
            latitude=location.latitude,
            longitude=location.longitude,
        )

        # -----------------------------------------------------
        # 6. CREATE PFZ DESTINATION
        # -----------------------------------------------------

        destination = {
            "coastal_reference": (
                selected_pfz["coastal_reference"]
            ),
            "latitude": selected_pfz["latitude"],
            "longitude": selected_pfz["longitude"],
        }

        # -----------------------------------------------------
        # 7. CREATE ROUTE REQUEST
        # -----------------------------------------------------

        request = RouteRequest(
            start=start,
            destination=destination,
        )

        # -----------------------------------------------------
        # 8. GENERATE ROUTES
        # -----------------------------------------------------

        result = self.generate_routes(
            request=request,
            time=requested_time,
            max_routes=max_routes,
            rows=rows,
            columns=columns,
        )

        # -----------------------------------------------------
        # 9. UPDATE AGENT STATE
        # -----------------------------------------------------

        return {
            **state,
            "route_required": True,
            "route_result": result.model_dump(),
        }