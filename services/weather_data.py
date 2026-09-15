from api.weather.weather import get_open_meteo_data


# Cache weather data for the current request/location/time
_weather_cache = {}


async def _get_weather_data(
    latitude: float,
    longitude: float,
    time: str
) -> dict:
    key = (round(latitude, 4), round(longitude, 4), time)

    if key not in _weather_cache:
        _weather_cache[key] = await get_open_meteo_data(
            latitude,
            longitude,
            time
        )

    return _weather_cache[key]


async def get_temperature(
    latitude: float,
    longitude: float,
    time: str
) -> float:

    data = await _get_weather_data(latitude, longitude, time)
    return data["temperature"]


async def get_wind_speed(
    latitude: float,
    longitude: float,
    time: str
) -> float:

    data = await _get_weather_data(latitude, longitude, time)
    return data["wind_speed"]


async def get_wind_direction(
    latitude: float,
    longitude: float,
    time: str
) -> int:

    data = await _get_weather_data(latitude, longitude, time)
    return data["wind_direction"]


async def get_wind_gust(
    latitude: float,
    longitude: float,
    time: str
) -> float:

    data = await _get_weather_data(latitude, longitude, time)
    return data["wind_gust"]


async def get_visibility(
    latitude: float,
    longitude: float,
    time: str
) -> float:

    data = await _get_weather_data(latitude, longitude, time)
    return data["visibility"]


async def get_precipitation(
    latitude: float,
    longitude: float,
    time: str
) -> float:

    data = await _get_weather_data(latitude, longitude, time)
    return data["precipitation"]


async def get_weather_code(
    latitude: float,
    longitude: float,
    time: str
) -> int:

    data = await _get_weather_data(latitude, longitude, time)
    return data["weather_code"]


async def get_weather_condition(
    latitude: float,
    longitude: float,
    time: str
) -> str:

    data = await _get_weather_data(latitude, longitude, time)
    return data["weather_condition"]


async def get_thunderstorm(
    latitude: float,
    longitude: float,
    time: str
) -> bool:

    data = await _get_weather_data(latitude, longitude, time)
    return data["thunderstorm"]