from api.marine.marine import get_marine_data, get_marine_warning

# marine tools

def get_wave_height(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["wave_height"]


def get_wave_direction(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["wave_direction"]


def get_wave_period(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["wave_period"]


def get_swell_wave_height(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["swell_wave_height"]


def get_swell_wave_direction(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["swell_wave_direction"]


def get_swell_wave_period(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["swell_wave_period"]


def get_ocean_current_velocity(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["ocean_current_velocity"]


def get_ocean_current_direction(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["ocean_current_direction"]


def get_sea_surface_temperature(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["sea_surface_temperature"]


def get_sea_level_height(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_marine_data(latitude, longitude, time)
    return data["sea_level_height_msl"]

def is_marine_warning(
    latitude: float,
    longitude: float
) -> bool:

    data = get_marine_warning(
        latitude,
        longitude
    )

    return data["warning"]

def get_high_wave_alert(
    latitude: float,
    longitude: float
):

    data = get_marine_warning(
        latitude,
        longitude
    )

    warning = data.get("high_wave_warning")

    if warning:
        return warning.get("Alert")

    return None

def get_high_wave_warning_message(
    latitude: float,
    longitude: float
):

    data = get_marine_warning(
        latitude,
        longitude
    )

    warning = data.get("high_wave_warning")

    if warning:
        return warning.get("Message")

    return None

def get_high_wave_warning_color(
    latitude: float,
    longitude: float
):

    data = get_marine_warning(
        latitude,
        longitude
    )

    warning = data.get("high_wave_warning")

    if warning:
        return warning.get("Color")

    return None

