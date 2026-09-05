from ai.engines.risk_engine.main import run_risk_engine
from services.location.marine_zones import is_protected, is_restricted

from services.weather_data import (
    get_wind_speed,
    get_wind_direction,
    get_visibility,
    get_precipitation,
    get_weather_condition,
    get_thunderstorm
)

from services.marine_data import (
    get_wave_height,
    get_wave_direction,
    get_wave_period,
    get_swell_wave_height,
    get_swell_wave_direction,
    get_swell_wave_period,
    get_ocean_current_velocity,
    get_ocean_current_direction,
    get_sea_surface_temperature,
    get_sea_level_height,
    get_marine_warning_level
)

def get_geo_data(latitude, longitude):
    return {
        "latitude": latitude,
        "longitude": longitude,
        "restricted_area": is_restricted(latitude, longitude),
        "protected_area": is_protected(latitude, longitude)
    }


def build_risk_input(node, time):
    latitude = node["latitude"]
    longitude = node["longitude"]

    marine_warning = get_marine_warning_level(
        latitude,
        longitude
    )

    if marine_warning is None:
        marine_warning = "NONE"
    else:
        marine_warning = marine_warning.upper()

    return {
        "request": {
            "request_id": node["node_id"],
            "requires_route": False,
            "forecast_hours": 24
        },
        "marine": {
            "wave_height": get_wave_height(latitude, longitude, time),
            "wave_period": get_wave_period(latitude, longitude, time),
            "wave_direction": get_wave_direction(latitude, longitude, time),
            "swell_wave_height": get_swell_wave_height(latitude, longitude, time),
            "swell_wave_period": get_swell_wave_period(latitude, longitude, time),
            "swell_wave_direction": get_swell_wave_direction(latitude, longitude, time),
            "ocean_current_velocity": get_ocean_current_velocity(latitude, longitude, time),
            "ocean_current_direction": get_ocean_current_direction(latitude, longitude, time),
            "sea_surface_temperature": get_sea_surface_temperature(latitude, longitude, time),
            "sea_level_height_msl": get_sea_level_height(latitude, longitude, time),
            "marine_warning": marine_warning
        },
        "weather": {
            "wind_speed": get_wind_speed(latitude, longitude, time),
            "wind_direction": get_wind_direction(latitude, longitude, time),
            "wave_height": get_wave_height(latitude, longitude, time),
            "visibility": get_visibility(latitude, longitude, time),
            "precipitation": get_precipitation(latitude, longitude, time),
            "lightning": get_thunderstorm(latitude, longitude, time),
            "condition": get_weather_condition(latitude, longitude, time)
        },
        "geo": get_geo_data(latitude, longitude)
    }
def evaluate_node(node, time):
    risk_input = build_risk_input(node, time)

    agent_data = {
        node["node_id"]: {
            time: risk_input
        }
    }

    result = run_risk_engine(agent_data)

    risk_result = result["ranked_results"][0]
    risk_score = risk_result["risk_score"]

    return {
        "node_id": node["node_id"],
        "risk_score": risk_score,
        "safe": risk_score <= 60
    }
def process_grid(k7_input):
    results = []

    time = k7_input["time"]

    for node in k7_input["nodes"]:
        result = evaluate_node(node, time)
        results.append(result)

    return results