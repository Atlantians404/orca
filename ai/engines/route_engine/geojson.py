from shapely.geometry import mapping, LineString


def linestring_to_geojson(
    route: LineString
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
        "properties": {}
    }