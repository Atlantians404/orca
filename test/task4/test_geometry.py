import pytest

from shapely.geometry import Polygon

from ai.engines.route_engine.geometry import (
    create_linestring,
    zone_to_polygon,
    route_intersects_polygon,
    validate_route,
)


def test_create_linestring():

    coordinates = [
        (12.90, 80.30),
        (12.95, 80.35),
        (13.00, 80.40),
    ]

    line = create_linestring(
        coordinates
    )

    assert line.geom_type == "LineString"

    assert len(line.coords) == 3


def test_create_linestring_requires_two_points():

    with pytest.raises(ValueError):

        create_linestring(
            [(12.90, 80.30)]
        )


def test_zone_to_polygon():

    zone = {
        "id": "ZONE001",
        "name": "Restricted Zone",
        "coordinates": [
            [12.90, 80.30],
            [12.90, 80.40],
            [13.00, 80.40],
            [13.00, 80.30],
            [12.90, 80.30],
        ],
    }

    polygon = zone_to_polygon(zone)

    assert isinstance(
        polygon,
        Polygon,
    )

    assert polygon.is_valid


def test_route_intersects_polygon():

    route = create_linestring(
        [
            (12.90, 80.30),
            (13.00, 80.40),
        ]
    )

    polygon = Polygon([
    (80.34, 12.94),
    (80.36, 12.94),
    (80.36, 12.96),
    (80.34, 12.96),
    ])
    

    assert route_intersects_polygon(
        route,
        polygon
    ) is True


def test_route_does_not_intersect_polygon():

    route = create_linestring(
        [
            (12.90, 80.30),
            (12.92, 80.32),
        ]
    )

    polygon = Polygon(
        [
            (12.96, 80.36),
            (12.96, 80.38),
            (12.98, 80.38),
            (12.98, 80.36),
        ]
    )

    assert route_intersects_polygon(
        route,
        polygon
    ) is False


def test_validate_safe_route():

    route = create_linestring(
        [
            (12.90, 80.30),
            (12.92, 80.32),
        ]
    )

    polygon = Polygon(
        [
            (12.96, 80.36),
            (12.96, 80.38),
            (12.98, 80.38),
            (12.98, 80.36),
        ]
    )

    assert validate_route(
        route,
        [polygon]
    ) is True


def test_validate_unsafe_route():

    route = create_linestring(
        [
            (12.90, 80.30),
            (13.00, 80.40),
        ]
    )

    polygon = Polygon(
        [
            (80.34, 12.94),
            (80.36, 12.94),
            (80.36, 12.96),
            (80.34, 12.96),
        ]
    )

    assert validate_route(
        route,
        [polygon]
    ) is False


def test_validate_route_multiple_zones():

    route = create_linestring(
        [
            (12.90, 80.30),
            (13.00, 80.40),
        ]
    )

    polygon1 = Polygon(
        [
            (80.34, 12.94),
            (80.36, 12.94),
            (80.36, 12.96),
            (80.34, 12.96),
        ]
    )

    polygon2 = Polygon(
        [
            (80.42, 13.02),
            (80.44, 13.02),
            (80.44, 13.04),
            (80.42, 13.04),
        ]
    )

    assert validate_route(
        route,
        [polygon1, polygon2]
    ) is False