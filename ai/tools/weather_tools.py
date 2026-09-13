from langchain_core.tools import tool

from services.weather_data import (
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


@tool
async def temperature_tool(latitude: float, longitude: float, time: str) -> float:
    """Get the temperature at a location and time."""
    return await get_temperature(latitude, longitude, time)


@tool
async def wind_speed_tool(latitude: float, longitude: float, time: str) -> float:
    """Get the wind speed at a location and time."""
    return await get_wind_speed(latitude, longitude, time)


@tool
async def wind_direction_tool(latitude: float, longitude: float, time: str) -> int:
    """Get the wind direction at a location and time."""
    return await get_wind_direction(latitude, longitude, time)


@tool
async def wind_gust_tool(latitude: float, longitude: float, time: str) -> float:
    """Get the wind gust at a location and time."""
    return await get_wind_gust(latitude, longitude, time)


@tool
async def visibility_tool(latitude: float, longitude: float, time: str) -> float:
    """Get the visibility at a location and time."""
    return await get_visibility(latitude, longitude, time)


@tool
async def precipitation_tool(latitude: float, longitude: float, time: str) -> float:
    """Get the precipitation at a location and time."""
    return await get_precipitation(latitude, longitude, time)


@tool
async def weather_code_tool(latitude: float, longitude: float, time: str) -> int:
    """Get the weather code at a location and time."""
    return await get_weather_code(latitude, longitude, time)


@tool
async def weather_condition_tool(latitude: float, longitude: float, time: str) -> str:
    """Get the weather condition at a location and time."""
    return await get_weather_condition(latitude, longitude, time)


@tool
async def thunderstorm_tool(latitude: float, longitude: float, time: str) -> bool:
    """Check whether there is a thunderstorm at a location and time."""
    return await get_thunderstorm(latitude, longitude, time)