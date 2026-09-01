from typing import Any

from services.data_service import (
    get_temperature,
    get_wind_speed,
    get_wind_direction,
    get_wind_gust,
    get_visibility,
    get_precipitation,
    get_weather_code,
    get_weather_condition,
    get_thunderstorm,
)

from api.marine.marine import get_marine_data


def run_data_collection_agent(
    state: dict[str, Any]
) -> dict[str, Any]:
    """
    Collect weather and marine data for the selected PFZ.

    Input:
        AgentState containing selected_pfz and time_context.

    Output:
        Updated AgentState containing agent_data.
    """

    selected_pfz = state.get("selected_pfz")
    time_context = state.get("time_context")

    # No PFZ selected
    if selected_pfz is None:
        return {
            **state,
            "agent_data": {}
        }

    # Get PFZ coordinates
    latitude = selected_pfz.get("latitude")
    longitude = selected_pfz.get("longitude")

    if latitude is None or longitude is None:
        return {
            **state,
            "agent_data": {}
        }

    # Get requested time
    if time_context is None or not time_context.slots:
        return {
            **state,
            "agent_data": {}
        }

    slot = time_context.slots[0]

    requested_time = slot.date

    if slot.start_time:
        requested_time += f"T{slot.start_time}:00"

    # Collect weather data
    weather = {
        "temperature": get_temperature(
            latitude,
            longitude,
            requested_time
        ),
        "wind_speed": get_wind_speed(
            latitude,
            longitude,
            requested_time
        ),
        "wind_direction": get_wind_direction(
            latitude,
            longitude,
            requested_time
        ),
        "wind_gust": get_wind_gust(
            latitude,
            longitude,
            requested_time
        ),
        "visibility": get_visibility(
            latitude,
            longitude,
            requested_time
        ),
        "precipitation": get_precipitation(
            latitude,
            longitude,
            requested_time
        ),
        "weather_code": get_weather_code(
            latitude,
            longitude,
            requested_time
        ),
        "weather_condition": get_weather_condition(
            latitude,
            longitude,
            requested_time
        ),
        "thunderstorm": get_thunderstorm(
            latitude,
            longitude,
            requested_time
        )
    }

    # Collect marine data
    marine = get_marine_data(
        latitude,
        longitude,
        requested_time
    )

    # Prepare AgentState data
    agent_data = {
        "pfz": selected_pfz,
        "weather": weather,
        "marine": marine,
        "collection_location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "collection_time": requested_time
    }

    return {
        **state,
        "agent_data": agent_data
    }