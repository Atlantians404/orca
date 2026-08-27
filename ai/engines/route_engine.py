import math 
class RouteEngine:

    @staticmethod
    def validate_coordinates(
        latitude: float,
        longitude: float
    ) -> bool:
        """
        Validate latitude and longitude.

        Latitude: -90 to 90
        Longitude: -180 to 180
        """

        return (
            -90 <= latitude <= 90
            and
            -180 <= longitude <= 180
        )

    
    @staticmethod
    def calculate_distance(
        point_a: tuple[float, float],
        point_b: tuple[float, float]
    ) -> float:

        lat1, lon1 = point_a
        lat2, lon2 = point_b

        if not RouteEngine.validate_coordinates(lat1, lon1):
            raise ValueError("Invalid coordinates for point A")

        if not RouteEngine.validate_coordinates(lat2, lon2):
            raise ValueError("Invalid coordinates for point B")

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