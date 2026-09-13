from langchain_core.tools import tool

from services.location.marine_zones import (
    is_protected,
    is_restricted,
)


@tool
async def protected_zone_tool(
    latitude: float,
    longitude: float,
) -> bool:
    """Check whether a location is inside a protected marine zone."""
    return await is_protected(latitude, longitude)


@tool
async def restricted_zone_tool(
    latitude: float,
    longitude: float,
) -> bool:
    """Check whether a location is inside a restricted marine zone."""
    return await is_restricted(latitude, longitude)