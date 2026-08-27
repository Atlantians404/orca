from shapely.geometry import Point

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