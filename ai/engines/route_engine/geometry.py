from shapely.geometry import Point, LineString, Polygon


def create_point(
    latitude: float,
    longitude: float
) -> Point:
    """
    Create a Shapely Point.

    Shapely uses:
        (x, y) = (longitude, latitude)
    """

    return Point(longitude, latitude)


def create_linestring(
    coordinates: list[tuple[float, float]]
) -> LineString:
    """
    Create a LineString from
    (latitude, longitude) coordinates.
    """

    return LineString(
        [
            (longitude, latitude)
            for latitude, longitude in coordinates
        ]
    )


def create_polygon(
    coordinates: list[tuple[float, float]]
) -> Polygon:
    """
    Create a Polygon from
    (latitude, longitude) coordinates.
    """

    return Polygon(
        [
            (longitude, latitude)
            for latitude, longitude in coordinates
        ]
    )