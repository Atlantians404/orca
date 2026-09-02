from ai.engines.route_engine.geometry import (
    create_linestring,
)

from ai.engines.route_engine.geojson import (
    linestring_to_geojson,
)


def test_linestring_to_geojson():

    route = create_linestring(
        [
            (12.90, 80.30),
            (12.90, 80.35),
            (12.95, 80.35)
        ]
    )

    result = linestring_to_geojson(route)

    assert result["type"] == "Feature"

    assert result["geometry"]["type"] == "LineString"

    assert result["geometry"]["coordinates"] == [
        [80.30, 12.90],
        [80.35, 12.90],
        [80.35, 12.95]
    ]