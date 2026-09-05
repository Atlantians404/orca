import math

from .graph import (
    MarineGraph,
    create_route_grid,
    connect_grid,
    find_nearest_node,
    path_to_coordinates,
)

from .algorithms import generate_candidate_paths

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

        Coordinates are:

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
    # FIND ROUTE NODES
    # =========================================================

    @staticmethod
    def find_route_nodes(
        graph: MarineGraph,
        start: Coordinate,
        destination: Coordinate,
    ) -> tuple[str, str]:
        """
        Find the grid nodes nearest to the
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
    # GENERATE CANDIDATE ROUTES
    # =========================================================

    def generate_routes(
        self,
        request: RouteRequest,
        max_routes: int = 3,
        rows: int = 10,
        columns: int = 10,
    ) -> CandidateRoutes:
        """
        Generate multiple candidate routes between
        the start location and selected PFZ.
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
        # 2. FIND START AND DESTINATION GRID NODES
        # -----------------------------------------------------

        start_node, destination_node = (
            self.find_route_nodes(
                graph,
                request.start,
                request.destination,
            )
        )

        # -----------------------------------------------------
        # 3. GENERATE CANDIDATE PATHS
        # -----------------------------------------------------

        candidates = generate_candidate_paths(
            graph,
            start_node,
            destination_node,
            max_routes=max_routes,
        )

        # -----------------------------------------------------
        # 4. CONVERT PATHS INTO ROUTE RESULTS
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
        # 5. RETURN CANDIDATE ROUTES
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
    ) -> CandidateRoutes:
        """
        Main entry point for the Route Engine.
        """

        return self.generate_routes(
            request=request,
            max_routes=max_routes,
            rows=rows,
            columns=columns,
        )