import httpx

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_condition(weather_code):

    conditions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    return conditions.get(weather_code, "Unknown")


def is_thunderstorm(weather_code):

    return weather_code in [95, 96, 99]


async def get_location_time(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m",
        "timezone": "auto"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
        WEATHER_URL,
        params=params
        )

    response.raise_for_status()

    data = response.json()

    return (
        data.get("current", {}).get("time"),
        data.get("timezone")
    )


async def get_open_meteo_data(latitude, longitude, time=None):
  
    if time is None:
        time, timezone = await get_location_time(
            latitude,
            longitude
        )
    else:
        _, timezone = await get_location_time(
            latitude,
            longitude
        )

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "visibility",
            "precipitation",
            "weather_code"
        ],
        "timezone": "auto",
        "start_hour": time,
        "end_hour": time
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
        WEATHER_URL,
        params=weather_params
        )

    response.raise_for_status()

    data = response.json()

    hourly = data.get("hourly", {})

    weather_code = hourly.get(
        "weather_code",
        [None]
    )[0]

    return {
        "latitude": latitude,
        "longitude": longitude,
        "time": hourly.get(
            "time",
            [time]
        )[0],

        "timezone": timezone,

        "temperature": hourly.get(
            "temperature_2m",
            [None]
        )[0],

        "wind_speed": hourly.get(
            "wind_speed_10m",
            [None]
        )[0],

        "wind_direction": hourly.get(
            "wind_direction_10m",
            [None]
        )[0],

        "wind_gust": hourly.get(
            "wind_gusts_10m",
            [None]
        )[0],

        "visibility": hourly.get(
            "visibility",
            [None]
        )[0],

        "precipitation": hourly.get(
            "precipitation",
            [None]
        )[0],

        "weather_code": weather_code,

        "weather_condition": get_weather_condition(
            weather_code
        ),

        "thunderstorm": is_thunderstorm(
            weather_code
        )
    }
