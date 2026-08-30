from api.weather.weather import get_open_meteo_data

# weather tools
def get_temperature(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["temperature_2m"]

def get_wind_speed(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["wind_speed_10m"]


def get_wind_direction(
    latitude: float,
    longitude: float,
    time: str
) -> int:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["wind_direction_10m"]


def get_wind_gust(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["wind_gusts_10m"]


def get_visibility(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["visibility"]


def get_precipitation(
    latitude: float,
    longitude: float,
    time: str
) -> float:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["precipitation"]


def get_weather_code(
    latitude: float,
    longitude: float,
    time: str
) -> int:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["weather_code"]


def get_weather_condition(
    latitude: float,
    longitude: float,
    time: str
) -> str:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["weather_condition"]


def get_thunderstorm(
    latitude: float,
    longitude: float,
    time: str
) -> bool:
    data = get_open_meteo_data(latitude, longitude, time)
    return data["weather"]["thunderstorm"]
