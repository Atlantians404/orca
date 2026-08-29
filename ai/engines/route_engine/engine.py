import math
import json
from pathlib import Path
from .validator import validate_coordinates
from .graph import find_nearest_node
from .schemas import RouteRequest, RouteResult, Waypoint

from .graph import (
    create_grid,
    connect_grid,
    apply_zone_constraints,
    path_to_coordinates,
)

from .geometry import (
    create_linestring,
    zone_to_polygon,
    validate_route,
)

from .pathfinding import astar

class RouteEngine:

    @staticmethod
    def calculate_distance(
        point_a: tuple[float, float],
        point_b: tuple[float, float]
    ) -> float:
        """
        Calculate distance between two coordinates
        using the Haversine formula.

        Coordinates are provided as:

            (latitude, longitude)

        Returns:
            Distance in kilometers.
        """

        lat1, lon1 = point_a
        lat2, lon2 = point_b

        if not validate_coordinates(lat1, lon1):
            raise ValueError(
                "Invalid coordinates for point A"
            )

        if not validate_coordinates(lat2, lon2):
            raise ValueError(
                "Invalid coordinates for point B"
            )

        earth_radius_km = 6371.0

        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        delta_lat = lat2 - lat1
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

        return earth_radius_km * c
    
    @staticmethod
    def load_marine_data() -> dict:
        """
        Load dummy marine data from JSON.
        """

        data_path = (
            Path(__file__).parent
            / "dummy_data"
            / "marine_data.json"
        )

        with open(data_path, "r", encoding="utf-8") as file:
            return json.load(file)
    
    @staticmethod
    def find_nearest_pfz(
        latitude: float,
        longitude: float
    ) -> dict:

        if not validate_coordinates(
            latitude,
            longitude
        ):
            raise ValueError("Invalid coordinates")

        data = RouteEngine.load_marine_data()

        pfz_locations = data["pfz_locations"]

        nearest_pfz = None
        shortest_distance = float("inf")

        for pfz in pfz_locations:

            distance = RouteEngine.calculate_distance(
                (latitude, longitude),
                (
                    pfz["latitude"],
                    pfz["longitude"]
                )
            )

            if distance < shortest_distance:
                shortest_distance = distance
                nearest_pfz = pfz

        return {
            "pfz": nearest_pfz,
            "distance_km": shortest_distance
        }
    @staticmethod
    def find_route(
        request: RouteRequest | None = None,
        *,
        start_latitude: float | None = None,
        start_longitude: float | None = None,
        goal_latitude: float | None = None,
        goal_longitude: float | None = None,
        restricted_zones: list | None = None
    ) -> RouteResult | dict:

        if request is None:
            if not validate_coordinates(start_latitude, start_longitude):
                raise ValueError("Invalid start coordinates")
            if not validate_coordinates(goal_latitude, goal_longitude):
                raise ValueError("Invalid goal coordinates")

            graph = create_grid(
                start_latitude=start_latitude,
                start_longitude=start_longitude,
                rows=3,
                columns=3,
                latitude_step=0.05,
                longitude_step=0.05
            )

            connect_grid(graph, rows=3, columns=3)

            start_node = find_nearest_node(graph, start_latitude, start_longitude)
            goal_node = find_nearest_node(graph, goal_latitude, goal_longitude)

            polygons = []
            if restricted_zones:
                for zone in restricted_zones:
                    polygon = zone_to_polygon(zone)
                    polygons.append(polygon)
                    apply_zone_constraints(graph, polygon)

            path, distance = astar(graph, start_node, goal_node)
            coordinates = path_to_coordinates(graph, path)
            route = create_linestring(coordinates)

            if not validate_route(route, polygons):
                raise ValueError("Generated route intersects a restricted zone")

            return {
                "path": path,
                "distance_km": distance,
                "coordinates": coordinates,
                "geojson": {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [longitude, latitude]
                            for latitude, longitude in coordinates
                        ]
                    },
                    "properties": {}
                }
            }

        start = request.start
        destination = request.destination

        # Create demo grid
        graph = create_grid(
            start_latitude=start.latitude,
            start_longitude=start.longitude,
            rows=3,
            columns=3,
            latitude_step=0.05,
            longitude_step=0.05
        )

        # Connect nodes
        connect_grid(
            graph,
            rows=3,
            columns=3
        )

        # Find nearest graph nodes
        start_node = find_nearest_node(
            graph,
            start.latitude,
            start.longitude
        )

        goal_node = find_nearest_node(
            graph,
            destination.latitude,
            destination.longitude
        )

        # Apply restricted zones
        polygons = []

        if request.constraints.avoid_restricted_zones:
            if hasattr(request.constraints, 'restricted_zones'):
                for zone in request.constraints.restricted_zones:
                    polygon = zone_to_polygon(zone)
                    polygons.append(polygon)

                    apply_zone_constraints(
                        graph,
                        polygon
                    )

        # Run A*
        path, distance = astar(
            graph,
            start_node,
            goal_node
        )

        # Convert node IDs → coordinates
        coordinates = path_to_coordinates(
            graph,
            path
        )

        # Convert to Shapely LineString
        route = create_linestring(
            coordinates
        )

        # Final validation
        if not validate_route(
            route,
            polygons
        ):
            raise ValueError(
                "Generated route intersects "
                "a restricted zone"
            )

        # Convert coordinates into waypoints
        waypoints = [
            Waypoint(
                latitude=latitude,
                longitude=longitude
            )
            for latitude, longitude in coordinates[1:-1]
        ]

        return RouteResult(
            pfz_id=destination.pfz_id,

            start=start,

            destination=Waypoint(
                latitude=destination.latitude,
                longitude=destination.longitude
            ),

            waypoints=waypoints,

            distance_km=distance,

            geojson={
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            longitude,
                            latitude
                        ]
                        for latitude, longitude in coordinates
                    ]
                },
                "properties": {
                    "pfz_id": destination.pfz_id
                }
            }
        )