import pytest 
from ai.engines.route_engine import RouteEngine


def test_valid_coordinates():

    assert RouteEngine.validate_coordinates(
        13.0827,
        80.2707
    ) is True


def test_invalid_latitude():

    assert RouteEngine.validate_coordinates(
        100,
        80
    ) is False


def test_invalid_longitude():

    assert RouteEngine.validate_coordinates(
        13,
        200
    ) is False


def test_boundary_coordinates():

    assert RouteEngine.validate_coordinates(
        90,
        180
    ) is True

def test_same_point_distance():

    distance = RouteEngine.calculate_distance(
        (13.0827, 80.2707),
        (13.0827, 80.2707)
    )

    assert distance == pytest.approx(0, abs=0.001)

def test_distance_is_positive():

    distance = RouteEngine.calculate_distance(
        (13.0827, 80.2707),
        (12.9249, 80.1000)
    )

    assert distance > 0

def test_distance_is_symmetric():

    point_a = (13.0827, 80.2707)
    point_b = (12.9249, 80.1000)

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

def test_invalid_point_a():

    with pytest.raises(ValueError):

        RouteEngine.calculate_distance(
            (100, 80),
            (13, 80)
        )
def test_invalid_point_b():

    with pytest.raises(ValueError):

        RouteEngine.calculate_distance(
            (13, 80),
            (100, 80)
        )
