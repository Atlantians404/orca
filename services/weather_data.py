from api.weather.weather import get_open_meteo_data


def get_temperature(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["temperature"]


def get_wind_speed(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["wind_speed"]


def get_wind_direction(
    latitude: float,
    longitude: float,
    time: str
) -> int:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["wind_direction"]


def get_wind_gust(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["wind_gust"]


def get_visibility(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["visibility"]


def get_precipitation(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["precipitation"]


def get_weather_code(
    latitude: float,
    longitude: float,
    time: str
) -> int:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather_code"]


def get_weather_condition(
    latitude: float,
    longitude: float,
    time: str
) -> str:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather_condition"]


def get_thunderstorm(
    latitude: float,
    longitude: float,
    time: str
) -> bool:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["thunderstorm"]