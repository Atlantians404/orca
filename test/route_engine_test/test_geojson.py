import pytest

from shapely.geometry import LineString

from ai.engines.route_engine.geometry import (
    linestring_to_geojson,
)


# =========================================================
# BASIC GEOJSON TEST
# =========================================================

def test_linestring_to_geojson():

    route = LineString([
        (80.27, 13.08),
        (80.28, 13.09),
        (80.29, 13.10),
    ])

    result = linestring_to_geojson(route)

    assert isinstance(result, dict)

    assert result["type"] == "Feature"

    assert result["geometry"]["type"] == "LineString"

    assert "coordinates" in result["geometry"]

    assert isinstance(
        result["geometry"]["coordinates"],
        list,
    )


# =========================================================
# COORDINATE TEST
# =========================================================

def test_geojson_contains_correct_coordinates():

    route = LineString([
        (80.27, 13.08),
        (80.28, 13.09),
        (80.29, 13.10),
    ])

    result = linestring_to_geojson(route)

    coordinates = result["geometry"]["coordinates"]

    assert coordinates == [
        [80.27, 13.08],
        [80.28, 13.09],
        [80.29, 13.10],
    ]


# =========================================================
# COORDINATE ORDER TEST
# =========================================================

def test_geojson_uses_longitude_latitude_order():

    route = LineString([
        (80.27, 13.08),
        (80.30, 13.11),
    ])

    result = linestring_to_geojson(route)

    coordinates = result["geometry"]["coordinates"]

    # GeoJSON uses:
    # [longitude, latitude]

    assert coordinates[0][0] == pytest.approx(
        80.27
    )

    assert coordinates[0][1] == pytest.approx(
        13.08
    )

    assert coordinates[1][0] == pytest.approx(
        80.30
    )

    assert coordinates[1][1] == pytest.approx(
        13.11
    )


# =========================================================
# PROPERTIES TEST
# =========================================================

def test_geojson_contains_properties():

    route = LineString([
        (80.27, 13.08),
        (80.28, 13.09),
    ])

    result = linestring_to_geojson(route)

    assert "properties" in result

    assert result["properties"] == {}


# =========================================================
# MINIMUM TWO POINTS
# =========================================================

def test_geojson_two_points():

    route = LineString([
        (80.27, 13.08),
        (80.28, 13.09),
    ])

    result = linestring_to_geojson(route)

    coordinates = result["geometry"]["coordinates"]

    assert len(coordinates) == 2


# =========================================================
# MULTIPLE POINTS
# =========================================================

def test_geojson_multiple_points():

    route = LineString([
        (80.27, 13.08),
        (80.28, 13.09),
        (80.29, 13.10),
        (80.30, 13.11),
        (80.31, 13.12),
    ])

    result = linestring_to_geojson(route)

    coordinates = result["geometry"]["coordinates"]

    assert len(coordinates) == 5


# =========================================================
# GEOJSON STRUCTURE
# =========================================================

def test_geojson_structure():

    route = LineString([
        (80.27, 13.08),
        (80.28, 13.09),
    ])

    result = linestring_to_geojson(route)

    assert set(result.keys()) == {
        "type",
        "geometry",
        "properties",
    }

    assert set(result["geometry"].keys()) == {
        "type",
        "coordinates",
    }


# =========================================================
# COORDINATES ARE LISTS
# =========================================================

def test_geojson_coordinates_are_lists():

    route = LineString([
        (80.27, 13.08),
        (80.28, 13.09),
    ])

    result = linestring_to_geojson(route)

    coordinates = result["geometry"]["coordinates"]

    for coordinate in coordinates:

        assert isinstance(
            coordinate,
            list,
        )

        assert len(coordinate) == 2


# =========================================================
# GEOJSON IS NOT EMPTY
# =========================================================

def test_geojson_is_not_empty():

    route = LineString([
        (80.27, 13.08),
        (80.28, 13.09),
    ])

    result = linestring_to_geojson(route)

    assert result
    assert result["geometry"]
    assert result["geometry"]["coordinates"]