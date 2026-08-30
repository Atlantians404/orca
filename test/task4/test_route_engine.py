import pytest

from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import (
    Coordinate,
    RouteDestination,
    RouteConstraints,
    RouteRequest,
)


# =========================================================
# HELPER
# =========================================================

def create_request(
    start_latitude=12.90,
    start_longitude=80.30,
    destination_latitude=13.00,
    destination_longitude=80.40,
    pfz_id="PFZ001",
    restricted_zones=None,
):
    """
    Create a standard RouteRequest for testing.
    """

    constraints = RouteConstraints(
        avoid_restricted_zones=True,
        restricted_zones=(
            restricted_zones
            if restricted_zones is not None
            else []
        ),
    )

    return RouteRequest(
        start=Coordinate(
            latitude=start_latitude,
            longitude=start_longitude,
        ),
        destination=RouteDestination(
            pfz_id=pfz_id,
            latitude=destination_latitude,
            longitude=destination_longitude,
        ),
        constraints=constraints,
    )


# =========================================================
# DISTANCE TESTS
# =========================================================

def test_same_point_distance():

    distance = RouteEngine.calculate_distance(
        (13.0827, 80.2707),
        (13.0827, 80.2707),
    )

    assert distance == pytest.approx(
        0,
        abs=0.001,
    )


def test_distance_positive():

    distance = RouteEngine.calculate_distance(
        (13.0827, 80.2707),
        (13.1400, 80.4300),
    )

    assert distance > 0


def test_distance_symmetric():

    point_a = (
        13.0827,
        80.2707,
    )

    point_b = (
        13.1400,
        80.4300,
    )

    distance_ab = RouteEngine.calculate_distance(
        point_a,
        point_b,
    )

    distance_ba = RouteEngine.calculate_distance(
        point_b,
        point_a,
    )

    assert distance_ab == pytest.approx(
        distance_ba,
        abs=0.001,
    )


def test_invalid_point_a():

    with pytest.raises(ValueError):

        RouteEngine.calculate_distance(
            (100, 80),
            (13, 80),
        )


def test_invalid_point_b():

    with pytest.raises(ValueError):

        RouteEngine.calculate_distance(
            (13, 80),
            (100, 80),
        )


# =========================================================
# MARINE DATA TESTS
# =========================================================

def test_load_marine_data():

    data = RouteEngine.load_marine_data()

    assert isinstance(data, dict)

    assert "ports" in data

    assert "pfz_locations" in data

    assert isinstance(
        data["pfz_locations"],
        list,
    )

    assert len(
        data["pfz_locations"]
    ) == 5


# =========================================================
# PFZ TESTS
# =========================================================

def test_find_nearest_pfz():

    result = RouteEngine.find_nearest_pfz(
        13.0827,
        80.2707,
    )

    assert result["pfz"] is not None

    assert result["distance_km"] > 0

    assert "id" in result["pfz"]

    assert "latitude" in result["pfz"]

    assert "longitude" in result["pfz"]


def test_find_nearest_pfz_invalid_coordinates():

    with pytest.raises(ValueError):

        RouteEngine.find_nearest_pfz(
            100,
            80,
        )


# =========================================================
# SINGLE ROUTE TESTS
# =========================================================

def test_find_route():

    request = create_request()

    result = RouteEngine.find_route(
        request
    )

    assert result is not None

    assert result.pfz_id == "PFZ001"

    assert result.distance_km > 0

    assert result.start.latitude == pytest.approx(
        12.90
    )

    assert result.start.longitude == pytest.approx(
        80.30
    )

    assert result.destination.latitude == pytest.approx(
        13.00
    )

    assert result.destination.longitude == pytest.approx(
        80.40
    )


def test_find_route_has_waypoints():

    request = create_request()

    result = RouteEngine.find_route(
        request
    )

    assert isinstance(
        result.waypoints,
        list,
    )

    assert len(
        result.waypoints
    ) >= 1


def test_find_route_geojson():

    request = create_request()

    result = RouteEngine.find_route(
        request
    )

    assert result.geojson["type"] == "Feature"

    assert (
        result.geojson["geometry"]["type"]
        == "LineString"
    )

    coordinates = (
        result.geojson["geometry"]["coordinates"]
    )

    assert len(coordinates) >= 2


def test_find_route_invalid_start():

    request = create_request(
        start_latitude=100,
        start_longitude=80.30,
    )

    with pytest.raises(ValueError):

        RouteEngine.find_route(
            request
        )


def test_find_route_invalid_destination():

    request = create_request(
        destination_latitude=100,
        destination_longitude=80.40,
    )

    with pytest.raises(ValueError):

        RouteEngine.find_route(
            request
        )


# =========================================================
# CANDIDATE ROUTE TESTS
# =========================================================

def test_find_routes_returns_candidate_routes():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    assert result is not None

    assert result.pfz_id == "PFZ001"

    assert isinstance(
        result.routes,
        list,
    )

    assert len(result.routes) >= 1


def test_find_routes_generates_multiple_routes():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    assert len(result.routes) >= 2


def test_candidate_routes_have_unique_route_ids():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    route_ids = [
        route.route_id
        for route in result.routes
    ]

    assert len(route_ids) == len(
        set(route_ids)
    )


def test_candidate_routes_have_valid_distances():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    for route in result.routes:

        assert route.distance_km > 0


def test_candidate_routes_have_waypoints():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    for route in result.routes:

        assert isinstance(
            route.waypoints,
            list,
        )

        assert len(
            route.waypoints
        ) >= 1


def test_candidate_routes_have_geojson():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    for route in result.routes:

        assert route.geojson["type"] == "Feature"

        assert (
            route.geojson["geometry"]["type"]
            == "LineString"
        )

        assert len(
            route.geojson["geometry"]["coordinates"]
        ) >= 2


# =========================================================
# CANDIDATE ROUTE PATH DIFFERENCE
# =========================================================

def test_candidate_routes_are_different():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    route_coordinates = []

    for route in result.routes:

        coordinates = tuple(
            tuple(point)
            for point
            in route.geojson["geometry"]["coordinates"]
        )

        route_coordinates.append(
            coordinates
        )

    assert len(
        route_coordinates
    ) == len(
        set(route_coordinates)
    )


# =========================================================
# MAX ROUTES VALIDATION
# =========================================================

def test_max_routes_must_be_at_least_two():

    request = create_request()

    with pytest.raises(ValueError):

        RouteEngine.find_routes(
            request,
            max_routes=0,
        )


def test_two_candidate_routes():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=2,
    )

    assert len(result.routes) >= 1

    assert len(result.routes) <= 2


# =========================================================
# RESTRICTED ZONE TEST
# =========================================================

def test_find_route_with_restricted_zone():

    restricted_zone = {
        "id": "ZONE001",
        "name": "Restricted Zone",
        "coordinates": [
            [12.94, 80.34],
            [12.94, 80.36],
            [12.96, 80.36],
            [12.96, 80.34],
            [12.94, 80.34],
        ],
    }

    request = create_request(
        restricted_zones=[
            restricted_zone
        ]
    )

    result = RouteEngine.find_route(
        request
    )

    assert result is not None

    assert result.distance_km > 0

    assert result.geojson["type"] == "Feature"


# =========================================================
# MULTIPLE CANDIDATE ROUTES WITH RESTRICTION
# =========================================================

def test_candidate_routes_with_restricted_zone():

    restricted_zone = {
        "id": "ZONE001",
        "name": "Restricted Zone",
        "coordinates": [
            [12.94, 80.34],
            [12.94, 80.36],
            [12.96, 80.36],
            [12.96, 80.34],
            [12.94, 80.34],
        ],
    }

    request = create_request(
        restricted_zones=[
            restricted_zone
        ]
    )

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    assert result is not None

    assert len(result.routes) >= 1

    for route in result.routes:

        assert route.distance_km > 0

        assert (
            route.geojson["geometry"]["type"]
            == "LineString"
        )