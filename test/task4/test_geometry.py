from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
from ai.engines.route_engine.geometry import pfz_to_point
from ai.engines.route_engine.geometry import zone_to_polygon

from ai.engines.route_engine.geometry import (
    create_point,
)


def test_create_point():

    point = create_point(
        13.0827,
        80.2707
    )

    assert isinstance(point, Point)

    assert point.x == 80.2707
    assert point.y == 13.0827



from ai.engines.route_engine.geometry import (
    create_linestring,
)


def test_create_linestring():

    coordinates = [
        (13.0827, 80.2707),
        (13.1000, 80.3000),
        (13.1400, 80.4300)
    ]

    line = create_linestring(coordinates)

    assert isinstance(line, LineString)

    assert len(line.coords) == 3



from ai.engines.route_engine.geometry import (
    create_polygon,
)


def test_create_polygon():

    coordinates = [
        (12.95, 80.32),
        (12.95, 80.42),
        (13.05, 80.42),
        (13.05, 80.32),
        (12.95, 80.32)
    ]

    polygon = create_polygon(coordinates)

    assert isinstance(polygon, Polygon)

    assert polygon.is_valid

from ai.engines.route_engine.geometry import (
    create_point,
    create_polygon,
    point_inside_polygon,
)
def test_point_inside_polygon():

    polygon = create_polygon(
        [
            (12.95, 80.32),
            (12.95, 80.42),
            (13.05, 80.42),
            (13.05, 80.32),
            (12.95, 80.32)
        ]
    )

    point = create_point(
        13.00,
        80.37
    )

    assert point_inside_polygon(
        point,
        polygon
    ) is True

from ai.engines.route_engine.geometry import (
    create_linestring,
    create_polygon,
    route_intersects_polygon,
)

def test_route_intersects_polygon():

    polygon = create_polygon(
        [
            (12.95, 80.32),
            (12.95, 80.42),
            (13.05, 80.42),
            (13.05, 80.32),
            (12.95, 80.32)
        ]
    )

    route = create_linestring(
        [
            (12.90, 80.20),
            (13.00, 80.37),
            (13.10, 80.50)
        ]
    )

    assert route_intersects_polygon(
        route,
        polygon
    ) is True

def test_route_does_not_intersect_polygon():

    polygon = create_polygon(
        [
            (12.95, 80.32),
            (12.95, 80.42),
            (13.05, 80.42),
            (13.05, 80.32),
            (12.95, 80.32)
        ]
    )

    route = create_linestring(
        [
            (12.70, 80.10),
            (12.75, 80.15),
            (12.80, 80.20)
        ]
    )

    assert route_intersects_polygon(
        route,
        polygon
    ) is False

def test_pfz_to_point():

    pfz = {
        "id": "PFZ001",
        "latitude": 13.1400,
        "longitude": 80.4300,
        "depth_m": 42.0
    }

    point = pfz_to_point(pfz)

    assert point.x == 80.4300
    assert point.y == 13.1400

def test_zone_to_polygon():

    zone = {
        "id": "ZONE001",
        "name": "Restricted Zone A",
        "coordinates": [
            [12.95, 80.32],
            [12.95, 80.42],
            [13.05, 80.42],
            [13.05, 80.32],
            [12.95, 80.32]
        ]
    }

    polygon = zone_to_polygon(zone)

    assert polygon.is_valid
    assert polygon.area > 0

def test_pfz_inside_restricted_zone():

    zone = {
        "id": "ZONE001",
        "name": "Restricted Zone A",
        "coordinates": [
            [12.95, 80.32],
            [12.95, 80.42],
            [13.05, 80.42],
            [13.05, 80.32],
            [12.95, 80.32]
        ]
    }

    pfz = {
        "id": "PFZ_TEST",
        "latitude": 13.00,
        "longitude": 80.37
    }

    polygon = zone_to_polygon(zone)
    point = pfz_to_point(pfz)

    assert point_inside_polygon(
        point,
        polygon
    ) is True

