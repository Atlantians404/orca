from ai.engines.route_engine.engine import (
    RouteEngine,
)

from ai.engines.route_engine.schemas import (
    Coordinate,
    RouteDestination,
    RouteConstraints,
    RouteRequest,
)


def create_request():

    return RouteRequest(
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
        constraints=RouteConstraints(
            avoid_restricted_zones=True,
            restricted_zones=[],
        ),
    )


def test_route_integration():

    request = create_request()

    result = RouteEngine.find_route(
        request
    )

    assert result.pfz_id == "PFZ001"

    assert result.distance_km > 0

    assert result.start.latitude == 12.90

    assert result.destination.latitude == 13.00

    assert (
        result.geojson["type"]
        == "Feature"
    )

    assert (
        result.geojson["geometry"]["type"]
        == "LineString"
    )


def test_candidate_route_integration():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    assert result.pfz_id == "PFZ001"

    assert len(result.routes) >= 1

    assert len(result.routes) <= 3

    for route in result.routes:

        assert route.route_id is not None

        assert route.pfz_id == "PFZ001"

        assert route.distance_km > 0

        assert (
            route.geojson["type"]
            == "Feature"
        )

        assert (
            route.geojson["geometry"]["type"]
            == "LineString"
        )


def test_candidate_routes_are_distinct():

    request = create_request()

    result = RouteEngine.find_routes(
        request,
        max_routes=3,
    )

    paths = []

    for route in result.routes:

        coordinates = tuple(
            tuple(point)
            for point
            in route.geojson[
                "geometry"
            ]["coordinates"]
        )

        paths.append(coordinates)

    assert len(paths) == len(
        set(paths)
    )


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


def test_route_with_restricted_zone():

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
        constraints=RouteConstraints(
            avoid_restricted_zones=True,
            restricted_zones=[
                restricted_zone
            ],
        ),
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