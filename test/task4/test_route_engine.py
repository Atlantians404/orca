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

def test_load_marine_data():

    data = RouteEngine.load_marine_data()

    assert "ports" in data
    assert "pfz_locations" in data

    assert len(data["pfz_locations"]) == 5

def test_find_nearest_pfz():

    result = RouteEngine.find_nearest_pfz(
        13.0827,
        80.2707
    )

    assert result["pfz"] is not None

    assert result["pfz"]["id"] == "PFZ001"

    assert result["distance_km"] > 0

def test_find_nearest_pfz_invalid_coordinates():

    with pytest.raises(ValueError):

        RouteEngine.find_nearest_pfz(
            100,
            80
        )