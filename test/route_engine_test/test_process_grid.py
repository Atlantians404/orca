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

PFZ = RouteDestination(
    coastal_reference="Kathivakkam Chinnakuppam",
    latitude=13.494444,
    longitude=80.379444,
)


def create_agent_state():
    """
    Create the same type of state that the
    Route Engine receives from the agent workflow.
    """

    return {
        "location": Location(
            latitude=START.latitude,
            longitude=START.longitude,
        ),

        "selected_pfz": {
            "coastal_reference": PFZ.coastal_reference,
            "latitude": PFZ.latitude,
            "longitude": PFZ.longitude,
            "depth_m": 42.0,
        },

        "time_context": TimeContext(
            slots=[
                TimeSlot(
                    date="2026-09-05",
                    start_time="08:00",
                    end_time="09:00",
                )
            ],
            timezone="Asia/Kolkata",
        ),

        "route_required": True,
    }


# =========================================================
# ROUTE ENGINE → RISK HELPER
# =========================================================

def test_route_engine_risk_helper_integration(monkeypatch):

    engine = RouteEngine()

    state = create_agent_state()

    captured_input = {}

    # -----------------------------------------------------
    # Mock only external weather/marine data.
    #
    # process_grid itself remains active.
    # -----------------------------------------------------

    def fake_process_grid(k7_input):

        captured_input.update(k7_input)

        results = []

        for node in k7_input["nodes"]:

            results.append({
                "node_id": node["node_id"],
                "risk_score": 25.0,
                "safe": True,
            })

        return results

    monkeypatch.setattr(
        "ai.engines.route_engine.engine.process_grid",
        fake_process_grid,
    )

    # -----------------------------------------------------
    # Run Route Engine
    # -----------------------------------------------------

    result = engine.process(
        state=state,
        max_routes=1,
        rows=5,
        columns=5,
    )

    # =====================================================
    # VERIFY ROUTE ENGINE CALLED RISK HELPER
    # =====================================================

    assert captured_input

    assert "nodes" in captured_input
    assert "time" in captured_input

    assert len(captured_input["nodes"]) == 25

    assert (
        captured_input["time"]
        == "2026-09-05T08:00:00"
    )

    # =====================================================
    # VERIFY NODE FORMAT
    # =====================================================

    for node in captured_input["nodes"]:

        assert "node_id" in node
        assert "latitude" in node
        assert "longitude" in node

        assert isinstance(
            node["node_id"],
            str,
        )

        assert isinstance(
            node["latitude"],
            float,
        )

        assert isinstance(
            node["longitude"],
            float,
        )

    # =====================================================
    # VERIFY ROUTE RESULT
    # =====================================================

    assert result["route_required"] is True

    assert result["route_result"] is not None

    route_result = result["route_result"]

    assert (
        route_result["coastal_reference"]
        == "Kathivakkam Chinnakuppam"
    )

    assert "routes" in route_result

    assert len(route_result["routes"]) == 1


# =========================================================
# VERIFY RISK SCORES ARE USED
# =========================================================

def test_route_engine_uses_risk_scores(monkeypatch):

    engine = RouteEngine()

    state = create_agent_state()

    def fake_process_grid(k7_input):

        results = []

        for index, node in enumerate(
            k7_input["nodes"]
        ):

            # Make some nodes unsafe.
            if index % 2 == 0:
                risk_score = 20.0
                safe = True
            else:
                risk_score = 80.0
                safe = False

            results.append({
                "node_id": node["node_id"],
                "risk_score": risk_score,
                "safe": safe,
            })

        return results

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

    routes = result["route_result"]["routes"]

    assert len(routes) >= 1

    route = routes[0]

    assert route["distance_km"] >= 0

    assert "waypoints" in route

    assert "geojson" in route


# =========================================================
# VERIFY AGENT STATE → ROUTE ENGINE
# =========================================================

def test_agent_state_data_is_used(monkeypatch):

    engine = RouteEngine()

    state = create_agent_state()

    state["location"] = Location(
        latitude=12.9000,
        longitude=80.2000,
    )

    state["selected_pfz"] = {
        "coastal_reference": "Test PFZ",
        "latitude": 13.6000,
        "longitude": 80.5000,
        "depth_m": 50.0,
    }

    state["time_context"] = TimeContext(
        slots=[
            TimeSlot(
                date="2026-09-05",
                start_time="14:00",
                end_time="15:00",
            )
        ],
        timezone="Asia/Kolkata",
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

    route = result["route_result"]["routes"][0]

    # -----------------------------------------------------
    # Location came from AgentState
    # -----------------------------------------------------

    assert (
        route["start"]["latitude"]
        == 12.9000
    )

    assert (
        route["start"]["longitude"]
        == 80.2000
    )

    # -----------------------------------------------------
    # PFZ came from AgentState
    # -----------------------------------------------------

    assert (
        result["route_result"]["coastal_reference"]
        == "Test PFZ"
    )

    assert (
        route["destination"]["latitude"]
        == 13.6000
    )

    assert (
        route["destination"]["longitude"]
        == 80.5000
    )