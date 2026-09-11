from .schemas import Coordinate


def validate_coordinates(
    latitude: float | None,
    longitude: float | None,
) -> bool:
    if latitude is None or longitude is None:
        return False

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return False

    return (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    )


def validate_coordinate(
    coordinate: Coordinate,
) -> bool:
    return validate_coordinates(
        coordinate.latitude,
        coordinate.longitude,
    )


def validate_route_coordinates(
    coordinates: list[tuple[float, float]],
) -> bool:
    if not coordinates:
        return False

    return all(
        validate_coordinates(latitude, longitude)
        for latitude, longitude in coordinates
    )