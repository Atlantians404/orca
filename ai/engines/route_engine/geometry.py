from shapely.geometry import (
    Point,
    LineString,
    Polygon,
    mapping,
)


# =========================================================
# POINT
# =========================================================

def create_point(
    latitude: float,
    longitude: float,
) -> Point:
    """
    Create a Shapely Point.

    Application format:
        (latitude, longitude)

    Shapely format:
        (longitude, latitude)
    """

    return Point(
        longitude,
        latitude,
    )


# =========================================================
# LINESTRING
# =========================================================

def create_linestring(
    coordinates: list[tuple[float, float]],
) -> LineString:
    """
    Create a Shapely LineString.

    Input:
        [
            (latitude, longitude),
            ...
        ]

    Shapely internally uses:
        (longitude, latitude)
    """

    if len(coordinates) < 2:
        raise ValueError(
            "A LineString requires at least two points"
        )

    return LineString(
        [
            (longitude, latitude)
            for latitude, longitude in coordinates
        ]
    )


# =========================================================
# POLYGON
# =========================================================

def create_polygon(
    coordinates: list[tuple[float, float]],
) -> Polygon:
    """
    Create a Shapely Polygon.

    Input:
        (latitude, longitude)

    Shapely uses:
        (longitude, latitude)
    """

    if len(coordinates) < 3:
        raise ValueError(
            "A Polygon requires at least three points"
        )

    return Polygon(
        [
            (longitude, latitude)
            for latitude, longitude in coordinates
        ]
    )


# =========================================================
# POINT INSIDE POLYGON
# =========================================================

def point_inside_polygon(
    point: Point,
    polygon: Polygon,
) -> bool:
    """
    Check whether a point is inside a polygon.
    """

    return polygon.contains(point)


# =========================================================
# ROUTE INTERSECTION
# =========================================================

def route_intersects_polygon(
    route: LineString,
    polygon: Polygon,
) -> bool:
    """
    Check whether a route intersects a polygon.
    """

    return route.intersects(polygon)


# =========================================================
# PFZ TO POINT
# =========================================================

def pfz_to_point(
    pfz: dict,
) -> Point:
    """
    Convert a PFZ dictionary into a Shapely Point.
    """

    if "latitude" not in pfz:
        raise ValueError(
            "PFZ latitude is missing"
        )

    if "longitude" not in pfz:
        raise ValueError(
            "PFZ longitude is missing"
        )

    return create_point(
        pfz["latitude"],
        pfz["longitude"],
    )


# =========================================================
# ZONE TO POLYGON
# =========================================================

def zone_to_polygon(
    zone,
) -> Polygon:
    """
    Convert a restricted/protected zone
    into a Shapely Polygon.
    """

    if hasattr(zone, "coordinates"):

        coordinates = zone.coordinates

    elif isinstance(zone, dict):

        if "coordinates" not in zone:
            raise ValueError(
                "Zone coordinates are missing"
            )

        coordinates = zone["coordinates"]

    else:

        raise TypeError(
            "Zone must be a dictionary or an object "
            "with a coordinates attribute"
        )

    return create_polygon(
        coordinates
    )


# =========================================================
# ROUTE VALIDATION
# =========================================================

def validate_route(
    route: LineString,
    restricted_polygons: list[Polygon],
) -> bool:
    """
    Validate that a route does not intersect
    any restricted polygon.

    Restricted/protected-area handling is retained
    for future integration.
    """

    for polygon in restricted_polygons:

        if route.intersects(polygon):
            return False

    return True


# =========================================================
# LINESTRING → GEOJSON
# =========================================================

def linestring_to_geojson(
    route: LineString,
) -> dict:
    """
    Convert a Shapely LineString
    into a GeoJSON Feature.
    """

    geom = mapping(route)

    geom["coordinates"] = [
        list(coord)
        for coord in geom["coordinates"]
    ]

    return {
        "type": "Feature",
        "geometry": geom,
        "properties": {},
    }