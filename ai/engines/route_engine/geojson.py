from .geometry import create_linestring


def route_to_geojson(
    coordinates: list[tuple[float, float]],
) -> dict:

    line = create_linestring(
        coordinates
    )

    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    longitude,
                    latitude,
                ]
                for latitude, longitude
                in coordinates
            ],
        },
    }