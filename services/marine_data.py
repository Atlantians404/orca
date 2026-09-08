from api.marine.marine import get_marine_data, get_marine_warning

# marine tools

async def get_wave_height(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["wave_height"]


async def get_wave_direction(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["wave_direction"]


async def get_wave_period(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["wave_period"]


async def get_swell_wave_height(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["swell_wave_height"]


async def get_swell_wave_direction(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["swell_wave_direction"]


async def get_swell_wave_period(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["swell_wave_period"]


async def get_ocean_current_velocity(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["ocean_current_velocity"]


async def get_ocean_current_direction(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["ocean_current_direction"]


async def get_sea_surface_temperature(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["sea_surface_temperature"]


async def get_sea_level_height(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = await get_marine_data(latitude, longitude, time)
    return data["sea_level_height_msl"]

async def is_marine_warning(
    latitude: float,
    longitude: float
) -> bool:

    data = await get_marine_warning(
        latitude,
        longitude
    )

    return data["warning"]

async def get_marine_warning_level(
    latitude: float,
    longitude: float
) -> str | None:

    data = await get_marine_warning(
        latitude,
        longitude
    )

    warning = data.get("high_wave_warning")

    if not warning:
        return None

    alert = warning.get("Alert", "").lower()

    if "critical" in alert:
        return "critical"

    if "severe" in alert:
        return "severe"

    if "warning" in alert:
        return "warning"

    if "advisory" in alert:
        return "advisory"

    return None

async def get_high_wave_alert(
    latitude: float,
    longitude: float
):

    data = await get_marine_warning(
        latitude,
        longitude
    )

    warning = data.get("high_wave_warning")

    if warning:
        return warning.get("Alert")

    return None

async def get_high_wave_warning_message(
    latitude: float,
    longitude: float
):

    data = await get_marine_warning(
        latitude,
        longitude
    )

    warning = data.get("high_wave_warning")

    if warning:
        return warning.get("Message")

    return None

async def get_high_wave_warning_color(
    latitude: float,
    longitude: float
):

    data = await get_marine_warning(
        latitude,
        longitude
    )

    warning = data.get("high_wave_warning")

    if warning:
        return warning.get("Color")

    return None

