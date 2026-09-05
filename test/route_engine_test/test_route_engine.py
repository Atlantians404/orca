import pytest

from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import (
    Coordinate,
    RouteDestination,
    RouteRequest,
)
from ai.schemas.location import Location
from ai.schemas.time import TimeContext, TimeSlot


# =========================================================
# TEST DATA
# =========================================================

START = Coordinate(
    latitude=13.0827,
    longitude=80.2707,
)

DESTINATION = RouteDestination(
    coastal_reference="Kathivakkam Chinnakuppam",
    latitude=13.494444,
    longitude=80.379444,
)


def create_state():
    """
    Create the AgentState data required by
    RouteEngine.process().
    """

    return {
        "location": Location(
            latitude=13.0827,
            longitude=80.2707,
        ),

        "selected_pfz": {
            "coastal_reference": "Kathivakkam Chinnakuppam",
            "latitude": 13.494444,
            "longitude": 80.379444,
            "depth_m": 42.0,
        },

        "time_context": TimeContext(
            slots=[
                TimeSlot(
                    date="2026-09-05",
                    start_time="12:00",
                    end_time="13:00",
                )
            ],
            timezone="Asia/Kolkata",
        ),

        "route_required": True,
    }


# =========================================================
# HAVERSINE DISTANCE
# =========================================================

def test_calculate_distance():

    distance = RouteEngine.calculate_distance(
        (
            START.latitude,
            START.longitude,
        ),
        (
            DESTINATION.latitude,
            DESTINATION.longitude,
        ),
    )

    assert isinstance(distance, float)
    assert distance > 0


# =========================================================
# BUILD GRAPH
# =========================================================

def test_build_graph():

    graph = RouteEngine.build_graph(
        start=START,
        destination=Coordinate(
            latitude=DESTINATION.latitude,
            longitude=DESTINATION.longitude,
        ),
        rows=10,
        columns=10,
    )

    assert graph is not None
    assert len(graph.nodes) == 100
    assert len(graph.edges) == 100


# =========================================================
# FIND ROUTE NODES
# =========================================================

def test_find_route_nodes():

    engine = RouteEngine()

    graph = engine.build_graph(
        start=START,
        destination=Coordinate(
            latitude=DESTINATION.latitude,
            longitude=DESTINATION.longitude,
        ),
        rows=10,
        columns=10,
    )

    start_node, destination_node = (
        engine.find_route_nodes(
            graph,
            START,
            Coordinate(
                latitude=DESTINATION.latitude,
                longitude=DESTINATION.longitude,
            ),
        )
    )

    assert start_node in graph.nodes
    assert destination_node in graph.nodes
    assert start_node != destination_node


# =========================================================
# ROUTE REQUEST
# =========================================================

def test_route_request():

    request = RouteRequest(
        start=START,
        destination=DESTINATION,
    )

    assert request.start.latitude == 13.0827
    assert request.start.longitude == 80.2707

    assert (
        request.destination.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )


# =========================================================
# BUILD RISK INPUT
# =========================================================

def test_build_risk_input():

    engine = RouteEngine()

    graph = engine.build_graph(
        start=START,
        destination=Coordinate(
            latitude=DESTINATION.latitude,
            longitude=DESTINATION.longitude,
        ),
        rows=3,
        columns=3,
    )

    risk_input = engine.build_risk_input(
        graph=graph,
        time="2026-09-05T12:00:00",
    )

    assert "nodes" in risk_input
    assert "time" in risk_input

    assert (
        risk_input["time"]
        == "2026-09-05T12:00:00"
    )

    assert len(risk_input["nodes"]) == 9

    for node in risk_input["nodes"]:

        assert "node_id" in node
        assert "latitude" in node
        assert "longitude" in node


# =========================================================
# BUILD RISK SCORE MAP
# =========================================================

def test_build_risk_score_map():

    risk_results = [
        {
            "node_id": "N1",
            "risk_score": 20,
            "safe": True,
        },
        {
            "node_id": "N2",
            "risk_score": 55,
            "safe": True,
        },
        {
            "node_id": "N3",
            "risk_score": 80,
            "safe": False,
        },
    ]

    result = RouteEngine.build_risk_score_map(
        risk_results
    )

    assert result == {
        "N1": 20.0,
        "N2": 55.0,
        "N3": 80.0,
    }


# =========================================================
# CREATE ROUTE RESULT
# =========================================================

def test_create_route_result():

    engine = RouteEngine()

    graph = engine.build_graph(
        start=START,
        destination=Coordinate(
            latitude=DESTINATION.latitude,
            longitude=DESTINATION.longitude,
        ),
        rows=3,
        columns=3,
    )

    start_node, destination_node = (
        engine.find_route_nodes(
            graph,
            START,
            Coordinate(
                latitude=DESTINATION.latitude,
                longitude=DESTINATION.longitude,
            ),
        )
    )

    path = [
        start_node,
        destination_node,
    ]

    route = engine.create_route_result(
        graph=graph,
        path=path,
        distance=10.0,
        start=START,
        destination=Coordinate(
            latitude=DESTINATION.latitude,
            longitude=DESTINATION.longitude,
        ),
        coastal_reference=(
            "Kathivakkam Chinnakuppam"
        ),
        route_number=1,
    )

    assert route.route_id == "ROUTE_1"

    assert (
        route.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )

    assert route.distance_km == 10.0

    assert isinstance(
        route.waypoints,
        list,
    )

    assert isinstance(
        route.geojson,
        dict,
    )

    assert route.geojson["type"] == "Feature"


# =========================================================
# GENERATE ROUTES
# =========================================================

def test_generate_routes(monkeypatch):

    engine = RouteEngine()

    request = RouteRequest(
        start=START,
        destination=DESTINATION,
    )

    # -----------------------------------------------------
    # Mock Risk Helper
    # -----------------------------------------------------
    def fake_process_grid(k7_input):

        return [
            {
                "node_id": node["node_id"],
                "risk_score": 20.0,
                "safe": True,
            }
            for node in k7_input["nodes"]
        ]

    monkeypatch.setattr(
        "ai.engines.route_engine.engine.process_grid",
        fake_process_grid,
    )

    result = engine.generate_routes(
        request=request,
        time="2026-09-05T12:00:00",
        max_routes=3,
        rows=10,
        columns=10,
    )

    assert result is not None

    assert (
        result.coastal_reference
        == "Kathivakkam Chinnakuppam"
    )

    assert isinstance(
        result.routes,
        list,
    )

    assert len(result.routes) >= 1
    assert len(result.routes) <= 3


# =========================================================
# PROCESS - AGENT STATE
# =========================================================

def test_process(monkeypatch):

    engine = RouteEngine()

    state = create_state()

    # -----------------------------------------------------
    # Mock Risk Helper
    # -----------------------------------------------------
    def fake_process_grid(k7_input):

        return [
            {
                "node_id": node["node_id"],
                "risk_score": 20.0,
                "safe": True,
            }
            for node in k7_input["nodes"]
        ]

    monkeypatch.setattr(
        "ai.engines.route_engine.engine.process_grid",
        fake_process_grid,
    )

    result = engine.process(
        state=state,
        max_routes=3,
        rows=10,
        columns=10,
    )

    assert result is not None

    assert result["route_required"] is True

    assert "route_result" in result

    route_result = result["route_result"]

    assert (
        route_result["coastal_reference"]
        == "Kathivakkam Chinnakuppam"
    )

    assert "routes" in route_result

    assert len(route_result["routes"]) >= 1


# =========================================================
# PROCESS USES LOCATION
# =========================================================

def test_process_uses_location(monkeypatch):

    engine = RouteEngine()

    state = create_state()

    # Change user location
    state["location"] = Location(
        latitude=12.9000,
        longitude=80.2000,
    )

    def fake_process_grid(k7_input):

        return [
            {
                "node_id": node["node_id"],
                "risk_score": 10.0,
                "safe": True,
            }
            for node in k7_input["nodes"]
        ]

    monkeypatch.setattr(
        "ai.engines.route_engine.engine.process_grid",
        fake_process_grid,
    )

    result = engine.process(
        state=state,
        max_routes=1,
        rows=5,
        columns=5,
    )

    assert result["route_result"] is not None

    route = result["route_result"]["routes"][0]

    assert (
        route["start"]["latitude"]
        == 12.9000
    )

    assert (
        route["start"]["longitude"]
        == 80.2000
    )


# =========================================================
# PROCESS USES SELECTED PFZ
# =========================================================

def test_process_uses_selected_pfz(monkeypatch):

    engine = RouteEngine()

    state = create_state()

    state["selected_pfz"] = {
        "coastal_reference": "Test PFZ",
        "latitude": 13.6000,
        "longitude": 80.5000,
        "depth_m": 50.0,
    }

    def fake_process_grid(k7_input):

        return [
            {
                "node_id": node["node_id"],
                "risk_score": 15.0,
                "safe": True,
            }
            for node in k7_input["nodes"]
        ]

    monkeypatch.setattr(
        "ai.engines.route_engine.engine.process_grid",
        fake_process_grid,
    )

    result = engine.process(
        state=state,
        max_routes=1,
        rows=5,
        columns=5,
    )

    route_result = result["route_result"]

    assert (
        route_result["coastal_reference"]
        == "Test PFZ"
    )

    route = route_result["routes"][0]

    assert (
        route["destination"]["latitude"]
        == 13.6000
    )

    assert (
        route["destination"]["longitude"]
        == 80.5000
    )


# =========================================================
# PROCESS REQUIRES LOCATION
# =========================================================

def test_process_requires_location(monkeypatch):

    engine = RouteEngine()

    state = create_state()

    state["location"] = None

    with pytest.raises(
        ValueError,
        match="requires a location",
    ):

        engine.process(
            state=state,
        )


# =========================================================
# PROCESS REQUIRES PFZ
# =========================================================

def test_process_requires_selected_pfz():

    engine = RouteEngine()

    state = create_state()

    state["selected_pfz"] = None

    with pytest.raises(
        ValueError,
        match="requires a selected PFZ",
    ):

        engine.process(
            state=state,
        )


# =========================================================
# PROCESS REQUIRES TIME
# =========================================================

def test_process_requires_time_context():

    engine = RouteEngine()

    state = create_state()

    state["time_context"] = None

    with pytest.raises(
        ValueError,
        match="requires a time context",
    ):

        engine.process(
            state=state,
        )


# =========================================================
# INVALID MAX ROUTES
# =========================================================

def test_invalid_max_routes(monkeypatch):

    engine = RouteEngine()

    request = RouteRequest(
        start=START,
        destination=DESTINATION,
    )

    def fake_process_grid(k7_input):

        return [
            {
                "node_id": node["node_id"],
                "risk_score": 20.0,
                "safe": True,
            }
            for node in k7_input["nodes"]
        ]

    monkeypatch.setattr(
        "ai.engines.route_engine.engine.process_grid",
        fake_process_grid,
    )

    with pytest.raises(ValueError):

        engine.generate_routes(
            request=request,
            time="2026-09-05T12:00:00",
            max_routes=0,
            rows=5,
            columns=5,
        )


# =========================================================
# ROUTE GEOJSON
# =========================================================

def test_route_geojson(monkeypatch):

    engine = RouteEngine()

    state = create_state()

    def fake_process_grid(k7_input):

        return [
            {
                "node_id": node["node_id"],
                "risk_score": 20.0,
                "safe": True,
            }
            for node in k7_input["nodes"]
        ]

    monkeypatch.setattr(
        "ai.engines.route_engine.engine.process_grid",
        fake_process_grid,
    )

    result = engine.process(
        state=state,
        max_routes=1,
        rows=5,
        columns=5,
    )

    route = result["route_result"]["routes"][0]

    assert isinstance(
        route["geojson"],
        dict,
    )

    assert route["geojson"]["type"] == "Feature"

    assert (
        route["geojson"]["geometry"]["type"]
        == "LineString"
    )

    assert (
        len(
            route["geojson"]
            ["geometry"]
            ["coordinates"]
        )
        >= 2
    )


# =========================================================
# WAYPOINT VALIDATION
# =========================================================

def test_waypoints_are_valid(monkeypatch):

    engine = RouteEngine()

    state = create_state()

    def fake_process_grid(k7_input):

        return [
            {
                "node_id": node["node_id"],
                "risk_score": 20.0,
                "safe": True,
            }
            for node in k7_input["nodes"]
        ]

    monkeypatch.setattr(
        "ai.engines.route_engine.engine.process_grid",
        fake_process_grid,
    )

    result = engine.process(
        state=state,
        max_routes=1,
        rows=5,
        columns=5,
    )

    route = result["route_result"]["routes"][0]

    for waypoint in route["waypoints"]:

        assert -90 <= waypoint["latitude"] <= 90
        assert -180 <= waypoint["longitude"] <= 180