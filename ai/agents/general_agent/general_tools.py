from langchain_core.tools import tool

# =========================================================
# LOCATION SERVICES
# =========================================================

from services.location.place_to_coordinate import (
    get_coordinates,
)

from services.location.pfz_to_coordinate import (
    get_pfz_coordinates,
)

from services.location.marine_zones import (
    is_protected,
    is_restricted,
)


# =========================================================
# MARINE SERVICES
# =========================================================

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
    get_marine_warning_level,
    get_high_wave_alert,
    get_high_wave_warning_message,
    get_high_wave_warning_color,
)


# =========================================================
# WEATHER SERVICES
# =========================================================

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


# =========================================================
# LOCATION TOOLS
# =========================================================

@tool
def coordinates_tool(place: str) -> dict:
    """
    Convert a place name into latitude and longitude.

    Use this when the user mentions a location by name,
    such as Chennai or Pondicherry.
    """

    return get_coordinates(place)


@tool
def pfz_coordinates_tool(pfz_name: str) -> dict:
    """
    Get the latitude and longitude of a PFZ using its name.
    """

    return get_pfz_coordinates(pfz_name)


# =========================================================
# MARINE ZONE TOOLS
# =========================================================

@tool
def protected_zone_tool(
    latitude: float,
    longitude: float,
) -> bool:
    """
    Check whether a location is inside a protected marine zone.
    """

    return is_protected(
        latitude,
        longitude,
    )


@tool
def restricted_zone_tool(
    latitude: float,
    longitude: float,
) -> bool:
    """
    Check whether a location is inside a restricted marine zone.
    """

    return is_restricted(
        latitude,
        longitude,
    )


# =========================================================
# WAVE TOOLS
# =========================================================

@tool
def wave_height_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get wave height at a location and time.
    """

    return get_wave_height(
        latitude,
        longitude,
        time,
    )


@tool
def wave_direction_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get wave direction at a location and time.
    """

    return get_wave_direction(
        latitude,
        longitude,
        time,
    )


@tool
def wave_period_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get wave period at a location and time.
    """

    return get_wave_period(
        latitude,
        longitude,
        time,
    )


# =========================================================
# SWELL TOOLS
# =========================================================

@tool
def swell_wave_height_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get swell wave height at a location and time.
    """

    return get_swell_wave_height(
        latitude,
        longitude,
        time,
    )


@tool
def swell_wave_direction_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get swell wave direction at a location and time.
    """

    return get_swell_wave_direction(
        latitude,
        longitude,
        time,
    )


@tool
def swell_wave_period_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get swell wave period at a location and time.
    """

    return get_swell_wave_period(
        latitude,
        longitude,
        time,
    )


# =========================================================
# OCEAN CURRENT TOOLS
# =========================================================

@tool
def ocean_current_velocity_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get ocean current velocity at a location and time.
    """

    return get_ocean_current_velocity(
        latitude,
        longitude,
        time,
    )


@tool
def ocean_current_direction_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get ocean current direction at a location and time.
    """

    return get_ocean_current_direction(
        latitude,
        longitude,
        time,
    )


# =========================================================
# SEA CONDITION TOOLS
# =========================================================

@tool
def sea_surface_temperature_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get sea surface temperature at a location and time.
    """

    return get_sea_surface_temperature(
        latitude,
        longitude,
        time,
    )


@tool
def sea_level_height_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get sea level height at a location and time.
    """

    return get_sea_level_height(
        latitude,
        longitude,
        time,
    )


# =========================================================
# MARINE WARNING TOOLS
# =========================================================

@tool
def marine_warning_tool(
    latitude: float,
    longitude: float,
) -> bool:
    """
    Check whether a marine warning exists at a location.
    """

    return is_marine_warning(
        latitude,
        longitude,
    )


@tool
def marine_warning_level_tool(
    latitude: float,
    longitude: float,
) -> str | None:
    """
    Get the marine warning level at a location.
    """

    return get_marine_warning_level(
        latitude,
        longitude,
    )


@tool
def high_wave_alert_tool(
    latitude: float,
    longitude: float,
) -> str | None:
    """
    Get the high wave alert at a location.
    """

    return get_high_wave_alert(
        latitude,
        longitude,
    )


@tool
def high_wave_warning_message_tool(
    latitude: float,
    longitude: float,
) -> str | None:
    """
    Get the high wave warning message at a location.
    """

    return get_high_wave_warning_message(
        latitude,
        longitude,
    )


@tool
def high_wave_warning_color_tool(
    latitude: float,
    longitude: float,
) -> str | None:
    """
    Get the high wave warning color at a location.
    """

    return get_high_wave_warning_color(
        latitude,
        longitude,
    )


# =========================================================
# WEATHER TOOLS
# =========================================================

@tool
def temperature_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get air temperature at a location and time.
    """

    return get_temperature(
        latitude,
        longitude,
        time,
    )


@tool
def wind_speed_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get wind speed at a location and time.
    """

    return get_wind_speed(
        latitude,
        longitude,
        time,
    )


@tool
def wind_direction_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get wind direction at a location and time.
    """

    return get_wind_direction(
        latitude,
        longitude,
        time,
    )


@tool
def wind_gust_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get wind gust at a location and time.
    """

    return get_wind_gust(
        latitude,
        longitude,
        time,
    )


@tool
def visibility_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get visibility at a location and time.
    """

    return get_visibility(
        latitude,
        longitude,
        time,
    )


@tool
def precipitation_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> float:
    """
    Get precipitation at a location and time.
    """

    return get_precipitation(
        latitude,
        longitude,
        time,
    )


@tool
def weather_code_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> int:
    """
    Get weather code at a location and time.
    """

    return get_weather_code(
        latitude,
        longitude,
        time,
    )


@tool
def weather_condition_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> str:
    """
    Get the weather condition at a location and time.
    """

    return get_weather_condition(
        latitude,
        longitude,
        time,
    )


@tool
def thunderstorm_tool(
    latitude: float,
    longitude: float,
    time: str,
) -> bool:
    """
    Check whether thunderstorms are present at a location and time.
    """

    return get_thunderstorm(
        latitude,
        longitude,
        time,
    )


# =========================================================
# ALL GENERAL AGENT TOOLS
# =========================================================

GENERAL_TOOLS = [
    # Location
    coordinates_tool,
    pfz_coordinates_tool,

    # Zones
    protected_zone_tool,
    restricted_zone_tool,

    # Waves
    wave_height_tool,
    wave_direction_tool,
    wave_period_tool,

    # Swell
    swell_wave_height_tool,
    swell_wave_direction_tool,
    swell_wave_period_tool,

    # Ocean current
    ocean_current_velocity_tool,
    ocean_current_direction_tool,

    # Sea
    sea_surface_temperature_tool,
    sea_level_height_tool,

    # Marine warnings
    marine_warning_tool,
    marine_warning_level_tool,
    high_wave_alert_tool,
    high_wave_warning_message_tool,
    high_wave_warning_color_tool,

    # Weather
    temperature_tool,
    wind_speed_tool,
    wind_direction_tool,
    wind_gust_tool,
    visibility_tool,
    precipitation_tool,
    weather_code_tool,
    weather_condition_tool,
    thunderstorm_tool,
]