import pytest

from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import (
    Coordinate,
    RouteDestination,
    RouteConstraints,
    RouteRequest,
    RestrictedZone,
)


# =========================================================
# HELPER
# =========================================================

def create_request(
    start_latitude=12.90,
    start_longitude=80.30,
    destination_latitude=13.00,
    destination_longitude=80.40,
    coastal_reference="PFZ001",
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
            coastal_reference=coastal_reference,
            latitude=destination_latitude,
            longitude=destination_longitude,
        ),
        constraints=constraints,
    )


# =========================================================
# FIXTURE
# =========================================================

@pytest.fixture
def engine():
    return RouteEngine()


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


# =========================================================
# GRAPH BUILD TESTS
# =========================================================

def test_build_graph(engine):

    request = create_request()

    graph = engine.build_graph(
        start=request.start,
        destination=request.destination,
        rows=10,
        columns=10,
    )

    assert graph is not None
    assert len(graph.nodes) > 0
    assert len(graph.edges) > 0


def test_build_graph_contains_expected_grid_size(engine):

    request = create_request()

    graph = engine.build_graph(
        start=request.start,
        destination=request.destination,
        rows=5,
        columns=5,
    )

    assert len(graph.nodes) == 25


# =========================================================
# ROUTE NODE TESTS
# =========================================================

def test_find_route_nodes(engine):

    request = create_request()

    graph = engine.build_graph(
        start=request.start,
        destination=request.destination,
    )

    start_node, destination_node = (
        engine.find_route_nodes(
            graph,
            request.start,
            request.destination,
        )
    )

    assert start_node in graph.nodes
    assert destination_node in graph.nodes

    assert start_node != destination_node


# =========================================================
# SINGLE ROUTE GENERATION
# =========================================================

def test_generate_routes(engine):

    request = create_request()

    result = engine.generate_routes(
        request,
        max_routes=1,
    )

    assert result is not None

    assert result.coastal_reference == "PFZ001"

    assert isinstance(
        result.routes,
        list,
    )

    assert len(result.routes) >= 1


# =========================================================
# PROCESS TEST
# =========================================================

def test_process_returns_candidate_routes(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=3,
    )

    assert result is not None

    assert result.coastal_reference == "PFZ001"

    assert isinstance(
        result.routes,
        list,
    )

    assert len(result.routes) >= 1


# =========================================================
# ROUTE RESULT TESTS
# =========================================================

def test_route_result_contains_start_and_destination(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=1,
    )

    route = result.routes[0]

    assert route.start.latitude == pytest.approx(
        12.90
    )

    assert route.start.longitude == pytest.approx(
        80.30
    )

    assert route.destination.latitude == pytest.approx(
        13.00
    )

    assert route.destination.longitude == pytest.approx(
        80.40
    )


def test_route_result_has_positive_distance(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=1,
    )

    route = result.routes[0]

    assert route.distance_km > 0


def test_route_result_has_waypoints(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=1,
    )

    route = result.routes[0]

    assert isinstance(
        route.waypoints,
        list,
    )

    assert len(route.waypoints) >= 1


def test_route_result_waypoints_have_valid_coordinates(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=1,
    )

    route = result.routes[0]

    for waypoint in route.waypoints:

        assert -90 <= waypoint.latitude <= 90

        assert -180 <= waypoint.longitude <= 180


# =========================================================
# GEOJSON TESTS
# =========================================================

def test_route_result_geojson(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=1,
    )

    route = result.routes[0]

    assert route.geojson["type"] == "Feature"

    assert (
        route.geojson["geometry"]["type"]
        == "LineString"
    )

    coordinates = (
        route.geojson["geometry"]["coordinates"]
    )

    assert len(coordinates) >= 2


# =========================================================
# CANDIDATE ROUTE TESTS
# =========================================================

def test_multiple_candidate_routes(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=3,
    )

    assert len(result.routes) >= 1
    assert len(result.routes) <= 3


def test_candidate_routes_have_unique_ids(engine):

    request = create_request()

    result = engine.process(
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


def test_candidate_routes_have_valid_distances(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=3,
    )

    for route in result.routes:

        assert route.distance_km > 0


def test_candidate_routes_are_different(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=3,
    )

    route_coordinates = []

    for route in result.routes:

        coordinates = tuple(
            tuple(point)
            for point
            in route.geojson[
                "geometry"
            ][
                "coordinates"
            ]
        )

        route_coordinates.append(
            coordinates
        )

    assert len(route_coordinates) == len(
        set(route_coordinates)
    )


# =========================================================
# MAX ROUTES VALIDATION
# =========================================================

def test_max_routes_zero(engine):

    request = create_request()

    with pytest.raises(ValueError):

        engine.process(
            request,
            max_routes=0,
        )


def test_max_routes_one(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=1,
    )

    assert len(result.routes) >= 1
    assert len(result.routes) <= 1


def test_max_routes_two(engine):

    request = create_request()

    result = engine.process(
        request,
        max_routes=2,
    )

    assert len(result.routes) >= 1
    assert len(result.routes) <= 2


# =========================================================
# PFZ / COASTAL REFERENCE TEST
# =========================================================

def test_coastal_reference_is_preserved(engine):

    request = create_request(
        coastal_reference="Kathivakkam Chinnakuppam",
    )

    result = engine.process(
        request,
        max_routes=1,
    )

    assert (
        result.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )

    assert (
        result.routes[0].coastal_reference
        == "Kathivakkam Chinnakuppam"
    )


# =========================================================
# INVALID COORDINATE TESTS
# =========================================================

def test_invalid_start_latitude():

    with pytest.raises(ValueError):

        create_request(
            start_latitude=100,
        )


def test_invalid_start_longitude():

    with pytest.raises(ValueError):

        create_request(
            start_longitude=200,
        )


def test_invalid_destination_latitude():

    with pytest.raises(ValueError):

        create_request(
            destination_latitude=100,
        )


def test_invalid_destination_longitude():

    with pytest.raises(ValueError):

        create_request(
            destination_longitude=200,
        )


# =========================================================
# RESTRICTED ZONE TEST
# =========================================================

def test_restricted_zone_request():

    restricted_zone = RestrictedZone(
        name="Test Restricted Zone",
        state="Tamil Nadu",
        type="restricted",
        restriction_level="high",
        latitude=12.95,
        longitude=80.35,
    )

    request = create_request(
        restricted_zones=[
            restricted_zone
        ]
    )

    assert (
        request.constraints
        .avoid_restricted_zones
        is True
    )

    assert len(
        request.constraints
        .restricted_zones
    ) == 1


# =========================================================
# RISK HELPER INTEGRATION
# =========================================================

def test_risk_helper_input_format():

    """
    Verify the grid format expected by
    ai.tools.risk_helper.process_grid().
    """

    k7_input = {
        "nodes": [
            {
                "node_id": "N1",
                "latitude": 13.08,
                "longitude": 80.27,
            },
            {
                "node_id": "N2",
                "latitude": 13.09,
                "longitude": 80.28,
            },
        ],
        "time": "2026-09-05T08:00:00",
    }

    assert "nodes" in k7_input
    assert "time" in k7_input

    assert isinstance(
        k7_input["nodes"],
        list,
    )

    for node in k7_input["nodes"]:

        assert "node_id" in node
        assert "latitude" in node
        assert "longitude" in node


# =========================================================
# RISK HELPER PROCESS GRID
# =========================================================

def test_risk_helper_process_grid():

    from ai.tools.risk_helper import process_grid

    k7_input = {
        "nodes": [
            {
                "node_id": "N1",
                "latitude": 13.08,
                "longitude": 80.27,
            },
        ],
        "time": "2026-09-05T08:00:00",
    }

    result = process_grid(k7_input)

    assert result is not None
    assert isinstance(
        result,
        list,
    )

    assert len(result) == 1

    assert "node_id" in result[0]
    assert "risk_score" in result[0]
    assert "safe" in result[0]


# =========================================================
# ROUTE → RISK GRID FORMAT
# =========================================================

def test_route_nodes_can_be_converted_to_risk_input(
    engine,
):

    request = create_request()

    graph = engine.build_graph(
        start=request.start,
        destination=request.destination,
        rows=5,
        columns=5,
    )

    start_node, destination_node = (
        engine.find_route_nodes(
            graph,
            request.start,
            request.destination,
        )
    )

    path, distance = engine_path = (
        __import__(
            "ai.engines.route_engine.pathfinding",
            fromlist=["astar"],
        ).astar(
            graph,
            start_node,
            destination_node,
        )
    )

    assert len(path) >= 2
    assert distance > 0

    nodes = []

    for node_id in path:

        node = graph.nodes[node_id]

        nodes.append(
            {
                "node_id": node_id,
                "latitude": node.latitude,
                "longitude": node.longitude,
            }
        )

    k7_input = {
        "nodes": nodes,
        "time": "2026-09-05T08:00:00",
    }

    assert len(k7_input["nodes"]) == len(path)

    for node in k7_input["nodes"]:

        assert "node_id" in node
        assert "latitude" in node
        assert "longitude" in node

        assert -90 <= node["latitude"] <= 90
        assert -180 <= node["longitude"] <= 180