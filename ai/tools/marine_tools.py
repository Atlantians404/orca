from langchain_core.tools import tool

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
    is_marine_warning,
    get_high_wave_alert,
    get_high_wave_warning_message,
    get_high_wave_warning_color,
)


@tool
async def wave_height_tool(latitude: float, longitude: float, time: str) -> float:
    """Get wave height at a location and time."""
    return await get_wave_height(latitude, longitude, time)


@tool
async def wave_direction_tool(latitude: float, longitude: float, time: str) -> float:
    """Get wave direction at a location and time."""
    return await get_wave_direction(latitude, longitude, time)


@tool
async def wave_period_tool(latitude: float, longitude: float, time: str) -> float:
    """Get wave period at a location and time."""
    return await get_wave_period(latitude, longitude, time)


@tool
async def swell_wave_height_tool(latitude: float, longitude: float, time: str) -> float:
    """Get swell wave height at a location and time."""
    return await get_swell_wave_height(latitude, longitude, time)


@tool
async def swell_wave_direction_tool(latitude: float, longitude: float, time: str) -> float:
    """Get swell wave direction at a location and time."""
    return await get_swell_wave_direction(latitude, longitude, time)


@tool
async def swell_wave_period_tool(latitude: float, longitude: float, time: str) -> float:
    """Get swell wave period at a location and time."""
    return await get_swell_wave_period(latitude, longitude, time)


@tool
async def ocean_current_velocity_tool(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    """Get ocean current velocity at a location and time."""
    return await get_ocean_current_velocity(latitude, longitude, time)


@tool
async def ocean_current_direction_tool(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    """Get ocean current direction at a location and time."""
    return await get_ocean_current_direction(latitude, longitude, time)


@tool
async def sea_surface_temperature_tool(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    """Get sea surface temperature at a location and time."""
    return await get_sea_surface_temperature(latitude, longitude, time)


@tool
async def sea_level_height_tool(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    """Get sea level height at a location and time."""
    return await get_sea_level_height(latitude, longitude, time)


@tool
async def marine_warning_tool(latitude: float, longitude: float) -> bool:
    """Check whether a marine warning exists at a location."""
    return await is_marine_warning(latitude, longitude)


@tool
async def high_wave_alert_tool(latitude: float, longitude: float):
    """Get the high-wave alert at a location."""
    return await get_high_wave_alert(latitude, longitude)


@tool
async def high_wave_warning_message_tool(latitude: float, longitude: float):
    """Get the high-wave warning message at a location."""
    return await get_high_wave_warning_message(latitude, longitude)


@tool
async def high_wave_warning_color_tool(latitude: float, longitude: float):
    """Get the high-wave warning color at a location."""
    return await get_high_wave_warning_color(latitude, longitude)