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

def point_inside_polygon(
    point: Point,
    polygon: Polygon
) -> bool:
    """
    Check whether a point is inside a polygon.
    """

    return polygon.contains(point)

def route_intersects_polygon(
    route: LineString,
    polygon: Polygon
) -> bool:
    """
    Check whether a route intersects a polygon.
    """

    return route.intersects(polygon)

def pfz_to_point(pfz: dict) -> Point:
    """
    Convert a PFZ dictionary into a Shapely Point.
    """

    return create_point(
        pfz["latitude"],
        pfz["longitude"]
    )
def zone_to_polygon(zone: dict) -> Polygon:
    """
    Convert a zone dictionary into a Shapely Polygon.
    """

    return create_polygon(
        [
            tuple(coordinate)
            for coordinate in zone["coordinates"]
        ]
    )
