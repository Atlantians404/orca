from ai.engines.route_engine.schemas import (
    Coordinate,
    PFZ,
    RouteDestination,
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
        coastal_reference="Kathivakkam Chinnakuppam",
        latitude=13.494444,
        longitude=80.379444,
        depth_m=213.0,
    )

    assert (
        pfz.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )

    assert pfz.depth_m == 213.0


def test_pfz_optional_depth():

    pfz = PFZ(
        coastal_reference="Kathivakkam Chinnakuppam",
        latitude=13.494444,
        longitude=80.379444,
    )

    assert pfz.depth_m is None


def test_route_destination():

    destination = RouteDestination(
        coastal_reference="Kathivakkam Chinnakuppam",
        latitude=13.494444,
        longitude=80.379444,
    )

    assert (
        destination.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )


def test_route_request():

    request = RouteRequest(
        start=Coordinate(
            latitude=13.0827,
            longitude=80.2707,
        ),
        destination=RouteDestination(
            coastal_reference="Kathivakkam Chinnakuppam",
            latitude=13.494444,
            longitude=80.379444,
        ),
    )

    assert request.start.latitude == 13.0827

    assert (
        request.destination.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )

    assert request.time is None


def test_route_request_with_time():

    request = RouteRequest(
        start=Coordinate(
            latitude=13.0827,
            longitude=80.2707,
        ),
        destination=RouteDestination(
            coastal_reference="Kathivakkam Chinnakuppam",
            latitude=13.494444,
            longitude=80.379444,
        ),
        time="2026-09-04T14:00:00",
    )

    assert request.time == "2026-09-04T14:00:00"


def test_waypoint():

    waypoint = Waypoint(
        latitude=13.25,
        longitude=80.35,
    )

    assert waypoint.latitude == 13.25
    assert waypoint.longitude == 80.35


def test_route_result():

    result = RouteResult(
        route_id="ROUTE_1",
        coastal_reference="Kathivakkam Chinnakuppam",
        start=Coordinate(
            latitude=13.0827,
            longitude=80.2707,
        ),
        destination=Coordinate(
            latitude=13.494444,
            longitude=80.379444,
        ),
        waypoints=[
            Waypoint(
                latitude=13.25,
                longitude=80.35,
            )
        ],
        distance_km=15.5,
        geojson={
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [80.2707, 13.0827],
                    [80.35, 13.25],
                    [80.379444, 13.494444],
                ],
            },
        },
    )

    assert result.route_id == "ROUTE_1"

    assert (
        result.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )

    assert result.distance_km == 15.5

    assert len(result.waypoints) == 1


def test_route_result_route_id_optional():

    result = RouteResult(
        coastal_reference="Kathivakkam Chinnakuppam",
        start=Coordinate(
            latitude=13.0827,
            longitude=80.2707,
        ),
        destination=Coordinate(
            latitude=13.494444,
            longitude=80.379444,
        ),
        waypoints=[],
        distance_km=15.5,
        geojson={},
    )

    assert result.route_id is None


def test_candidate_routes():

    route1 = RouteResult(
        route_id="ROUTE_1",
        coastal_reference="Kathivakkam Chinnakuppam",
        start=Coordinate(
            latitude=13.0827,
            longitude=80.2707,
        ),
        destination=Coordinate(
            latitude=13.494444,
            longitude=80.379444,
        ),
        waypoints=[],
        distance_km=15.5,
        geojson={},
    )

    route2 = RouteResult(
        route_id="ROUTE_2",
        coastal_reference="Kathivakkam Chinnakuppam",
        start=Coordinate(
            latitude=13.0827,
            longitude=80.2707,
        ),
        destination=Coordinate(
            latitude=13.494444,
            longitude=80.379444,
        ),
        waypoints=[],
        distance_km=17.0,
        geojson={},
    )

    candidates = CandidateRoutes(
        coastal_reference="Kathivakkam Chinnakuppam",
        routes=[
            route1,
            route2,
        ],
    )

    assert (
        candidates.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )

    assert len(candidates.routes) == 2

    assert candidates.routes[0].route_id == "ROUTE_1"

    assert candidates.routes[1].route_id == "ROUTE_2"