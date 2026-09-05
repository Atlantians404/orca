import pytest

from ai.agents.data_collection_agent.data_collection_agent import (
    run_data_collection_agent,
)

from ai.engines.route_engine.engine import RouteEngine

from ai.schemas.location import Location

from ai.schemas.time import (
    TimeContext,
    TimeSlot,
)


# =========================================================
# TEST DATA
# =========================================================

START_LOCATION = Location(
    latitude=13.0500,
    longitude=80.2500,
)


SELECTED_PFZ = {
    "coastal_reference": "KATHIVAKKAM_01",
    "latitude": 13.494444,
    "longitude": 80.379444,
    "depth_m": 42.0,
}


TIME_CONTEXT = TimeContext(
    slots=[
        TimeSlot(
            date="2026-09-05",
            start_time="08:00",
            end_time="09:00",
        )
    ],
    timezone="Asia/Kolkata",
)


# =========================================================
# MOCK DATA SERVICES
# =========================================================

def mock_data_services(monkeypatch):

    module = (
        "ai.agents.data_collection_agent.data_collection_agent"
    )

    monkeypatch.setattr(
        f"{module}.get_temperature",
        lambda *args: 29.0,
    )

    monkeypatch.setattr(
        f"{module}.get_wind_speed",
        lambda *args: 15.0,
    )

    monkeypatch.setattr(
        f"{module}.get_wind_direction",
        lambda *args: 180.0,
    )

    monkeypatch.setattr(
        f"{module}.get_wind_gust",
        lambda *args: 20.0,
    )

    monkeypatch.setattr(
        f"{module}.get_visibility",
        lambda *args: 10.0,
    )

    monkeypatch.setattr(
        f"{module}.get_precipitation",
        lambda *args: 0.0,
    )

    monkeypatch.setattr(
        f"{module}.get_weather_code",
        lambda *args: 0,
    )

    monkeypatch.setattr(
        f"{module}.get_weather_condition",
        lambda *args: "CLEAR",
    )

    monkeypatch.setattr(
        f"{module}.get_thunderstorm",
        lambda *args: False,
    )

    monkeypatch.setattr(
        f"{module}.get_marine_data",
        lambda *args: {
            "wave_height": 1.2,
            "wave_period": 8.0,
            "wave_direction": 180.0,
            "swell_wave_height": 0.8,
            "swell_wave_period": 10.0,
            "swell_wave_direction": 200.0,
            "ocean_current_velocity": 0.5,
            "ocean_current_direction": 90.0,
            "sea_surface_temperature": 29.0,
            "sea_level_height_msl": 0.2,
        },
    )


# =========================================================
# CREATE AGENT STATE
# =========================================================

def create_state():

    return {
        "thread_id": "test-thread",

        "prompt": (
            "Find a safe route to the selected PFZ"
        ),

        "location": START_LOCATION,

        "time_context": TIME_CONTEXT,

        "selected_pfz": SELECTED_PFZ,

        "selected_pfz_id": (
            SELECTED_PFZ["coastal_reference"]
        ),

        "route_required": True,

        "workflow_status": "STARTED",
    }


# =========================================================
# TEST 1
# DATA COLLECTION UPDATES AGENT STATE
# =========================================================

def test_data_collection_updates_agent_state(
    monkeypatch,
):

    mock_data_services(monkeypatch)

    state = create_state()

    result = run_data_collection_agent(
        state
    )

    assert "agent_data" in result

    assert result["agent_data"]


# =========================================================
# TEST 2
# LOCATION IS PRESERVED
# =========================================================

def test_location_is_preserved(
    monkeypatch,
):

    mock_data_services(monkeypatch)

    state = create_state()

    result = run_data_collection_agent(
        state
    )

    assert result["location"] == START_LOCATION


# =========================================================
# TEST 3
# SELECTED PFZ IS PRESERVED
# =========================================================

def test_selected_pfz_is_preserved(
    monkeypatch,
):

    mock_data_services(monkeypatch)

    state = create_state()

    result = run_data_collection_agent(
        state
    )

    assert (
        result["selected_pfz"]
        == SELECTED_PFZ
    )

    assert (
        result["agent_data"]["pfz"]
        == SELECTED_PFZ
    )


# =========================================================
# TEST 4
# TIME CONTEXT IS PRESERVED
# =========================================================

def test_time_context_is_preserved(
    monkeypatch,
):

    mock_data_services(monkeypatch)

    state = create_state()

    result = run_data_collection_agent(
        state
    )

    assert (
        result["time_context"]
        == TIME_CONTEXT
    )

    assert (
        result["agent_data"]["collection_time"]
        == "2026-09-05T08:00:00"
    )


# =========================================================
# TEST 5
# WEATHER + MARINE DATA
# =========================================================

def test_agent_data_contains_weather_and_marine(
    monkeypatch,
):

    mock_data_services(monkeypatch)

    state = create_state()

    result = run_data_collection_agent(
        state
    )

    agent_data = result["agent_data"]

    assert "weather" in agent_data

    assert "marine" in agent_data

    assert (
        agent_data["weather"]["wind_speed"]
        == 15.0
    )

    assert (
        agent_data["marine"]["wave_height"]
        == 1.2
    )


# =========================================================
# TEST 6
# ROUTE ENGINE CAN READ AGENT STATE
# =========================================================

def test_route_engine_uses_agent_state():

    engine = RouteEngine()

    state = create_state()

    location = state["location"]

    pfz = state["selected_pfz"]

    assert location is not None

    assert pfz is not None

    # Start location

    assert (
        location.latitude
        == 13.0500
    )

    assert (
        location.longitude
        == 80.2500
    )

    # Destination PFZ

    assert (
        pfz["latitude"]
        == 13.494444
    )

    assert (
        pfz["longitude"]
        == 80.379444
    )


# =========================================================
# TEST 7
# COMPLETE AGENT STATE
# =========================================================

def test_complete_agent_state():

    state = create_state()

    assert state["location"] is not None

    assert state["selected_pfz"] is not None

    assert state["time_context"] is not None

    assert state["route_required"] is True

    assert (
        state["selected_pfz"][
            "coastal_reference"
        ]
        == "KATHIVAKKAM_01"
    )


# =========================================================
# TEST 8
# COLLECTION LOCATION MATCHES PFZ
# =========================================================

def test_collection_location_matches_pfz(
    monkeypatch,
):

    mock_data_services(monkeypatch)

    state = create_state()

    result = run_data_collection_agent(
        state
    )

    collection_location = (
        result["agent_data"]
        ["collection_location"]
    )

    assert (
        collection_location["latitude"]
        == SELECTED_PFZ["latitude"]
    )

    assert (
        collection_location["longitude"]
        == SELECTED_PFZ["longitude"]
    )


# =========================================================
# TEST 9
# NO PFZ → EMPTY AGENT DATA
# =========================================================

def test_no_selected_pfz(
    monkeypatch,
):

    mock_data_services(monkeypatch)

    state = create_state()

    state["selected_pfz"] = None

    result = run_data_collection_agent(
        state
    )

    assert result["agent_data"] == {}


# =========================================================
# TEST 10
# NO TIME CONTEXT → EMPTY AGENT DATA
# =========================================================

def test_no_time_context(
    monkeypatch,
):

    mock_data_services(monkeypatch)

    state = create_state()

    state["time_context"] = None

    result = run_data_collection_agent(
        state
    )

    assert result["agent_data"] == {}