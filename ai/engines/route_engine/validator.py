def validate_coordinates(
    latitude: float,
    longitude: float
) -> bool:
    """
    Validate geographic coordinates.

    Latitude:
        -90 to 90

    Longitude:
        -180 to 180
    """

    return (
        -90 <= latitude <= 90
        and
        -180 <= longitude <= 180
    )