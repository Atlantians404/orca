import pytest

from ai.engines.route_engine import RouteEngine
from ai.engines.route_engine.schemas import RouteRequest


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


def test_find_route():

    request = RouteRequest(
        start={
            "latitude": 12.90,
            "longitude": 80.30
        },

        destination={
            "pfz_id": "PFZ07",
            "latitude": 13.00,
            "longitude": 80.40
        },

        time="07:00"
    )

    result = RouteEngine.find_route(request)

    assert result.pfz_id == "PFZ07"

    assert result.start.latitude == 12.90
    assert result.start.longitude == 80.30

    assert result.destination.latitude == 13.00
    assert result.destination.longitude == 80.40

    assert result.distance_km > 0

    assert len(result.waypoints) >= 1

    assert result.geojson["type"] == "Feature"

    assert (
        result.geojson["geometry"]["type"]
        == "LineString"
    )


def test_find_route_with_restricted_zone():

    restricted_zone = {
        "id": "ZONE001",
        "name": "Restricted Zone",
        "coordinates": [
            [12.70, 80.10],
            [12.70, 80.20],
            [12.80, 80.20],
            [12.80, 80.10],
            [12.70, 80.10]
        ]
    }

    request = RouteRequest(
        start={
            "latitude": 12.90,
            "longitude": 80.30
        },

        destination={
            "pfz_id": "PFZ07",
            "latitude": 13.00,
            "longitude": 80.40
        },

        time="07:00",

        constraints={
            "avoid_restricted_zones": True,
            "restricted_zones": [
                restricted_zone
            ]
        }
    )

    result = RouteEngine.find_route(request)

    assert result.pfz_id == "PFZ07"

    assert result.distance_km > 0

    assert len(result.waypoints) >= 1


def test_find_route_invalid_start():

    request = RouteRequest(
        start={
            "latitude": 100,
            "longitude": 80.30
        },

        destination={
            "pfz_id": "PFZ07",
            "latitude": 13.00,
            "longitude": 80.40
        }
    )

    with pytest.raises(ValueError):

        RouteEngine.find_route(request)