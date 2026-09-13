from shapely.geometry import Point, LineString, Polygon
from shapely.geometry.base import BaseGeometry


def create_point(
    latitude: float,
    longitude: float,
) -> Point:
    """
    External format:
        latitude, longitude

    Shapely format:
        longitude, latitude
    """
    return Point(longitude, latitude)


def create_linestring(
    coordinates: list[tuple[float, float]],
) -> LineString:

    if len(coordinates) < 2:
        raise ValueError(
            "A LineString requires at least two coordinates."
        )

    shapely_coordinates = [
        (longitude, latitude)
        for latitude, longitude in coordinates
    ]

    return LineString(shapely_coordinates)


def create_polygon(
    coordinates: list[tuple[float, float]],
) -> Polygon:

    if len(coordinates) < 3:
        raise ValueError(
            "A Polygon requires at least three coordinates."
        )

    shapely_coordinates = [
        (longitude, latitude)
        for latitude, longitude in coordinates
    ]

    if shapely_coordinates[0] != shapely_coordinates[-1]:
        shapely_coordinates.append(
            shapely_coordinates[0]
        )

    return Polygon(shapely_coordinates)


def point_inside_polygon(
    latitude: float,
    longitude: float,
    polygon: Polygon,
) -> bool:

    point = create_point(
        latitude,
        longitude,
    )

    return polygon.contains(point)


def route_intersects_polygon(
    coordinates: list[tuple[float, float]],
    polygon: Polygon,
) -> bool:

    route = create_linestring(coordinates)

    return route.intersects(polygon)


def _get_zone_value(zone, key, default=None):

    if isinstance(zone, dict):
        return zone.get(key, default)

    return getattr(zone, key, default)


def zone_to_polygon(zone) -> Polygon:
    """
    Convert MongoDB/Pydantic zone data into
    a Shapely polygon.

    Supported formats:

    1. MongoDB GeoJSON:
       {
           "geometry": {
               "type": "Polygon",
               "coordinates": [...]
           }
       }

    2. Older test format:
       {
           "coordinates": [...]
       }
    """

    geometry = _get_zone_value(
        zone,
        "geometry",
    )

    if geometry:
        if hasattr(geometry, "model_dump"):
            geometry = geometry.model_dump()

        geometry_type = geometry.get("type")

        if geometry_type == "Polygon":
            raw_coordinates = geometry.get(
                "coordinates",
                [],
            )

            if not raw_coordinates:
                raise ValueError(
                    "Polygon geometry contains no coordinates."
                )

            # GeoJSON Polygon:
            # coordinates[0] = exterior ring
            ring = raw_coordinates[0]

            return create_polygon(
                [
                    tuple(coordinate)
                    for coordinate in ring
                ]
            )

    coordinates = _get_zone_value(
        zone,
        "coordinates",
    )

    if coordinates:
        return create_polygon(
            [
                tuple(coordinate)
                for coordinate in coordinates
            ]
        )

    raise ValueError(
        "Zone does not contain polygon coordinates."
    )


def validate_route(
    coordinates: list[tuple[float, float]],
    restricted_zones: list,
) -> bool:

    if len(coordinates) < 2:
        return False

    for zone in restricted_zones:

        polygon = zone_to_polygon(zone)

        if route_intersects_polygon(
            coordinates,
            polygon,
        ):
            return False

    return True