import pytest

from ai.tools.risk_helper import (
    build_risk_input,
    evaluate_node,
    process_grid,
    get_geo_data,
)


# =========================================================
# TEST NODE
# =========================================================

NODE = {
    "node_id": "N_1_1",
    "latitude": 13.2000,
    "longitude": 80.3000,
}

TIME = "2026-09-05T12:00:00"


# =========================================================
# BUILD RISK INPUT
# =========================================================

def test_build_risk_input(monkeypatch):

    # -----------------------------------------------------
    # Mock marine data
    # -----------------------------------------------------

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_wave_height",
        lambda lat, lon, time: 1.2,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_wave_direction",
        lambda lat, lon, time: 180.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_wave_period",
        lambda lat, lon, time: 8.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_swell_wave_height",
        lambda lat, lon, time: 0.8,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_swell_wave_direction",
        lambda lat, lon, time: 200.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_swell_wave_period",
        lambda lat, lon, time: 10.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_ocean_current_velocity",
        lambda lat, lon, time: 0.5,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_ocean_current_direction",
        lambda lat, lon, time: 90.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_sea_surface_temperature",
        lambda lat, lon, time: 29.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_sea_level_height",
        lambda lat, lon, time: 0.2,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_marine_warning_level",
        lambda lat, lon: None,
    )

    # -----------------------------------------------------
    # Mock weather data
    # -----------------------------------------------------

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_wind_speed",
        lambda lat, lon, time: 15.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_wind_direction",
        lambda lat, lon, time: 180.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_visibility",
        lambda lat, lon, time: 10.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_precipitation",
        lambda lat, lon, time: 0.0,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_thunderstorm",
        lambda lat, lon, time: False,
    )

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_weather_condition",
        lambda lat, lon, time: "CLEAR",
    )

    # -----------------------------------------------------
    # Execute
    # -----------------------------------------------------

    result = build_risk_input(
        NODE,
        TIME,
    )

    # -----------------------------------------------------
    # Validate structure
    # -----------------------------------------------------

    assert "request" in result
    assert "marine" in result
    assert "weather" in result
    assert "geo" in result

    assert (
        result["request"]["request_id"]
        == "N_1_1"
    )

    assert (
        result["request"]["requires_route"]
        is False
    )

    assert (
        result["marine"]["wave_height"]
        == 1.2
    )

    assert (
        result["weather"]["wind_speed"]
        == 15.0
    )

    assert (
        result["geo"]["latitude"]
        == 13.2000
    )

    assert (
        result["geo"]["longitude"]
        == 80.3000
    )


# =========================================================
# GEO DATA
# =========================================================

def test_geo_data():

    from ai.tools.risk_helper import get_geo_data

    result = get_geo_data(
        13.2000,
        80.3000,
    )

    assert result["latitude"] == 13.2000
    assert result["longitude"] == 80.3000

    # Restricted/protected areas are intentionally
    # kept as placeholders for future integration.
    assert result["restricted_area"] is False
    assert result["protected_area"] is False


# =========================================================
# BUILD RISK INPUT - MARINE WARNING
# =========================================================

def test_marine_warning(monkeypatch):

    monkeypatch.setattr(
        "ai.tools.risk_helper.get_marine_warning_level",
        lambda lat, lon: "WARNING",
    )

    # Weather/marine functions are mocked because
    # this test only checks warning normalization.

    for function_name in [
        "get_wave_height",
        "get_wave_period",
        "get_wave_direction",
        "get_swell_wave_height",
        "get_swell_wave_period",
        "get_swell_wave_direction",
        "get_ocean_current_velocity",
        "get_ocean_current_direction",
        "get_sea_surface_temperature",
        "get_sea_level_height",
        "get_wind_speed",
        "get_wind_direction",
        "get_visibility",
        "get_precipitation",
        "get_thunderstorm",
        "get_weather_condition",
    ]:

        monkeypatch.setattr(
            f"ai.tools.risk_helper.{function_name}",
            lambda *args: 0,
        )

    result = build_risk_input(
        NODE,
        TIME,
    )

    assert (
        result["marine"]["marine_warning"]
        == "WARNING"
    )


# =========================================================
# PROCESS GRID
# =========================================================

def test_process_grid(monkeypatch):

    # -----------------------------------------------------
    # Mock evaluate_node
    # -----------------------------------------------------

    def fake_evaluate_node(node, time):

        return {
            "node_id": node["node_id"],
            "risk_score": 25.0,
            "safe": True,
        }

    monkeypatch.setattr(
        "ai.tools.risk_helper.evaluate_node",
        fake_evaluate_node,
    )

    grid = {
        "time": TIME,
        "nodes": [
            {
                "node_id": "N_1_1",
                "latitude": 13.2,
                "longitude": 80.3,
            },
            {
                "node_id": "N_1_2",
                "latitude": 13.3,
                "longitude": 80.4,
            },
        ],
    }

    result = process_grid(grid)

    assert len(result) == 2

    assert result[0]["node_id"] == "N_1_1"
    assert result[0]["risk_score"] == 25.0
    assert result[0]["safe"] is True

    assert result[1]["node_id"] == "N_1_2"


# =========================================================
# EMPTY GRID
# =========================================================

def test_process_empty_grid():

    result = process_grid({
        "time": TIME,
        "nodes": [],
    })

    assert result == []