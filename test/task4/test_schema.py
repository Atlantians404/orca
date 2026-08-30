import pytest
from pydantic import ValidationError

from ai.engines.route_engine.schemas import (
    Coordinate,
    PFZ,
    RouteDestination,
    RestrictedZone,
    RouteConstraints,
    RouteRequest,
    Waypoint,
    RouteResult,
    CandidateRoutes,
)


def test_coordinate():

    coordinate = Coordinate(
        latitude=13.0827,
        longitude=80.2707,
    )

    assert coordinate.latitude == 13.0827
    assert coordinate.longitude == 80.2707


def test_pfz():

    pfz = PFZ(
        id="PFZ001",
        latitude=13.10,
        longitude=80.40,
        depth_m=50,
    )

    assert pfz.id == "PFZ001"
    assert pfz.depth_m == 50


def test_pfz_optional_depth():

    pfz = PFZ(
        id="PFZ001",
        latitude=13.10,
        longitude=80.40,
    )

    assert pfz.depth_m is None


def test_route_destination():

    destination = RouteDestination(
        pfz_id="PFZ001",
        latitude=13.10,
        longitude=80.40,
    )

    assert destination.pfz_id == "PFZ001"


def test_restricted_zone():

    zone = RestrictedZone(
        id="ZONE001",
        name="Restricted Zone",
        coordinates=[
            [12.90, 80.30],
            [12.90, 80.40],
            [13.00, 80.40],
            [13.00, 80.30],
            [12.90, 80.30],
        ],
    )

    assert zone.id == "ZONE001"

    assert len(zone.coordinates) == 5


def test_route_constraints_defaults():

    constraints = RouteConstraints()

    assert constraints.avoid_restricted_zones is True

    assert constraints.restricted_zones == []


def test_route_request():

    request = RouteRequest(
        start=Coordinate(
            latitude=12.90,
            longitude=80.30,
        ),
        destination=RouteDestination(
            pfz_id="PFZ001",
            latitude=13.00,
            longitude=80.40,
        ),
    )

    assert request.start.latitude == 12.90

    assert request.destination.pfz_id == "PFZ001"

    assert request.time is None


def test_route_request_with_time():

    request = RouteRequest(
        start=Coordinate(
            latitude=12.90,
            longitude=80.30,
        ),
        destination=RouteDestination(
            pfz_id="PFZ001",
            latitude=13.00,
            longitude=80.40,
        ),
        time="05:00",
    )

    assert request.time == "05:00"


def test_waypoint():

    waypoint = Waypoint(
        latitude=12.95,
        longitude=80.35,
    )

    assert waypoint.latitude == 12.95


def test_route_result():

    result = RouteResult(
        route_id="ROUTE_1",
        pfz_id="PFZ001",
        start=Coordinate(
            latitude=12.90,
            longitude=80.30,
        ),
        destination=Coordinate(
            latitude=13.00,
            longitude=80.40,
        ),
        waypoints=[
            Waypoint(
                latitude=12.95,
                longitude=80.35,
            )
        ],
        distance_km=15.5,
        geojson={
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [80.30, 12.90],
                    [80.35, 12.95],
                    [80.40, 13.00],
                ],
            },
        },
    )

    assert result.route_id == "ROUTE_1"

    assert result.distance_km == 15.5

    assert len(result.waypoints) == 1


def test_route_result_route_id_optional():

    result = RouteResult(
        pfz_id="PFZ001",
        start=Coordinate(
            latitude=12.90,
            longitude=80.30,
        ),
        destination=Coordinate(
            latitude=13.00,
            longitude=80.40,
        ),
        waypoints=[],
        distance_km=15.5,
        geojson={},
    )

    assert result.route_id is None


def test_candidate_routes():

    route1 = RouteResult(
        route_id="ROUTE_1",
        pfz_id="PFZ001",
        start=Coordinate(
            latitude=12.90,
            longitude=80.30,
        ),
        destination=Coordinate(
            latitude=13.00,
            longitude=80.40,
        ),
        waypoints=[],
        distance_km=15.5,
        geojson={},
    )

    route2 = RouteResult(
        route_id="ROUTE_2",
        pfz_id="PFZ001",
        start=Coordinate(
            latitude=12.90,
            longitude=80.30,
        ),
        destination=Coordinate(
            latitude=13.00,
            longitude=80.40,
        ),
        waypoints=[],
        distance_km=17.0,
        geojson={},
    )

    candidates = CandidateRoutes(
        pfz_id="PFZ001",
        routes=[
            route1,
            route2,
        ],
    )

    assert candidates.pfz_id == "PFZ001"

    assert len(candidates.routes) == 2

    assert candidates.routes[0].route_id == "ROUTE_1"

    assert candidates.routes[1].route_id == "ROUTE_2"