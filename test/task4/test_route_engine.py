import pytest

from ai.engines.route_engine import RouteEngine


def test_same_point_distance():

    distance = RouteEngine.calculate_distance(
        (13.0827, 80.2707),
        (13.0827, 80.2707)
    )

    assert distance == pytest.approx(
        0,
        abs=0.001
    )


def test_distance_positive():

    distance = RouteEngine.calculate_distance(
        (13.0827, 80.2707),
        (13.1400, 80.4300)
    )

    assert distance > 0


def test_distance_symmetric():

    point_a = (13.0827, 80.2707)
    point_b = (13.1400, 80.4300)

    distance_ab = RouteEngine.calculate_distance(
        point_a,
        point_b
    )

    distance_ba = RouteEngine.calculate_distance(
        point_b,
        point_a
    )

    assert distance_ab == pytest.approx(
        distance_ba,
        abs=0.001
    )


def test_invalid_point():

    with pytest.raises(ValueError):

        RouteEngine.calculate_distance(
            (100, 80),
            (13, 80)
        )