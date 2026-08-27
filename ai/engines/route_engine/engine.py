import math
import json
from pathlib import Path
from .validator import validate_coordinates


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