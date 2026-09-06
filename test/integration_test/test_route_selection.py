import pytest

from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import (
    Coordinate,
    RouteDestination,
    RouteRequest,
)
from ai.tools.risk_helper import process_grid


# =========================================================
# TEST DATA
# =========================================================

START = Coordinate(
    latitude=13.0500,
    longitude=80.2500,
)

DESTINATION = RouteDestination(
    coastal_reference="KATHIVAKKAM_01",
    latitude=13.494444,
    longitude=80.379444,
)


TEST_TIME = "2026-09-05T08:00:00"


# =========================================================
# ROUTE REQUEST
# =========================================================

def create_request():

    return RouteRequest(
        start=START,
        destination=DESTINATION,
    )


# =========================================================
# ROUTE → RISK HELPER NODES
# =========================================================

def build_nodes_from_route(route):

    nodes = []

    for index, waypoint in enumerate(route.waypoints):

        nodes.append(
            {
                "node_id": f"R{index + 1}",
                "latitude": waypoint.latitude,
                "longitude": waypoint.longitude,
            }
        )

    return nodes


# =========================================================
# GENERATE CANDIDATE ROUTES
# =========================================================

def test_generate_candidate_routes():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TEST_TIME,
        max_routes=3,
        rows=10,
        columns=10,
    )

    assert result is not None

    assert result.routes

    assert len(result.routes) <= 3


# =========================================================
# ROUTES HAVE VALID WAYPOINTS
# =========================================================

def test_routes_have_valid_waypoints():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TEST_TIME,
        max_routes=3,
        rows=10,
        columns=10,
    )

    assert len(result.routes) > 0

    for route in result.routes:

        assert route.waypoints is not None

        for waypoint in route.waypoints:

            assert -90 <= waypoint.latitude <= 90
            assert -180 <= waypoint.longitude <= 180


# =========================================================
# ROUTE → RISK HELPER
# =========================================================

def test_route_can_be_sent_to_risk_helper():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TEST_TIME,
        max_routes=3,
        rows=10,
        columns=10,
    )

    assert len(result.routes) > 0

    route = result.routes[0]

    nodes = build_nodes_from_route(route)

    if not nodes:
        pytest.skip(
            "Generated route contains no intermediate waypoints"
        )

    k7_input = {
        "nodes": nodes,
        "time": TEST_TIME,
    }

    risk_result = process_grid(k7_input)

    assert risk_result is not None

    assert isinstance(
        risk_result,
        list,
    )


# =========================================================
# RISK SCORE FOR EACH NODE
# =========================================================

def test_risk_scores_are_returned():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TEST_TIME,
        max_routes=3,
        rows=10,
        columns=10,
    )

    assert len(result.routes) > 0

    route = result.routes[0]

    nodes = build_nodes_from_route(route)

    if not nodes:
        pytest.skip(
            "Generated route contains no intermediate waypoints"
        )

    risk_result = process_grid(
        {
            "nodes": nodes,
            "time": TEST_TIME,
        }
    )

    for node_result in risk_result:

        assert "node_id" in node_result
        assert "risk_score" in node_result
        assert "safe" in node_result

        assert isinstance(
            node_result["risk_score"],
            (int, float),
        )

        assert 0 <= node_result["risk_score"] <= 100


# =========================================================
# SELECT LOWEST-RISK ROUTE
# =========================================================

def test_select_lowest_risk_route():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TEST_TIME,
        max_routes=3,
        rows=10,
        columns=10,
    )

    assert len(result.routes) > 0

    route_scores = []

    for route in result.routes:

        nodes = build_nodes_from_route(route)

        if not nodes:
            continue

        risk_result = process_grid(
            {
                "nodes": nodes,
                "time": TEST_TIME,
            }
        )

        if not risk_result:
            continue

        scores = [
            item["risk_score"]
            for item in risk_result
        ]

        average_risk = (
            sum(scores) / len(scores)
        )

        route_scores.append(
            {
                "route": route,
                "average_risk": average_risk,
            }
        )

    if not route_scores:
        pytest.skip(
            "No route contained risk-evaluable waypoints"
        )

    safest_route = min(
        route_scores,
        key=lambda item: item["average_risk"],
    )

    assert safest_route["route"] is not None

    assert 0 <= safest_route["average_risk"] <= 100


# =========================================================
# DESTINATION PFZ IS PRESERVED
# =========================================================

def test_destination_pfz_is_preserved():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TEST_TIME,
        max_routes=1,
        rows=10,
        columns=10,
    )

    assert (
        result.coastal_reference
        == DESTINATION.coastal_reference
    )