import requests


WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


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


def get_location_time(latitude, longitude):
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m",
        "timezone": "auto"
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return (
        data.get("current", {}).get("time"),
        data.get("timezone")
    )


def get_open_meteo_data(latitude, longitude, time=None):
    
    if time is None:
        time, timezone = get_location_time(
            latitude,
            longitude
        )
    else:
        _, timezone = get_location_time(
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

    weather_response = requests.get(
        WEATHER_URL,
        params=weather_params,
        timeout=10
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()

    weather_hourly = weather_data.get("hourly", {})

    weather_code = weather_hourly.get(
        "weather_code",
        [None]
    )[0]

    marine_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "wave_height",
            "wave_direction",
            "wave_period",
            "swell_wave_height",
            "swell_wave_direction",
            "swell_wave_period",
            "ocean_current_velocity",
            "ocean_current_direction",
            "sea_surface_temperature",
            "sea_level_height_msl"
        ],
        "timezone": "auto",
        "start_hour": time,
        "end_hour": time,
        "cell_selection": "sea"
    }

    marine_response = requests.get(
        MARINE_URL,
        params=marine_params,
        timeout=10
    )

    marine_response.raise_for_status()

    marine_data = marine_response.json()

    marine_hourly = marine_data.get("hourly", {})

    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "time": time,
            "timezone": timezone
        },

        "weather": {
            "time": weather_hourly.get(
                "time",
                [None]
            )[0],

            "temperature_2m": weather_hourly.get(
                "temperature_2m",
                [None]
            )[0],

            "wind_speed_10m": weather_hourly.get(
                "wind_speed_10m",
                [None]
            )[0],

            "wind_direction_10m": weather_hourly.get(
                "wind_direction_10m",
                [None]
            )[0],

            "wind_gusts_10m": weather_hourly.get(
                "wind_gusts_10m",
                [None]
            )[0],

            "visibility": weather_hourly.get(
                "visibility",
                [None]
            )[0],

            "precipitation": weather_hourly.get(
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
        },

        "marine": {
            "time": marine_hourly.get(
                "time",
                [None]
            )[0],

            "wave_height": marine_hourly.get(
                "wave_height",
                [None]
            )[0],

            "wave_direction": marine_hourly.get(
                "wave_direction",
                [None]
            )[0],

            "wave_period": marine_hourly.get(
                "wave_period",
                [None]
            )[0],

            "swell_wave_height": marine_hourly.get(
                "swell_wave_height",
                [None]
            )[0],

            "swell_wave_direction": marine_hourly.get(
                "swell_wave_direction",
                [None]
            )[0],

            "swell_wave_period": marine_hourly.get(
                "swell_wave_period",
                [None]
            )[0],

            "ocean_current_velocity": marine_hourly.get(
                "ocean_current_velocity",
                [None]
            )[0],

            "ocean_current_direction": marine_hourly.get(
                "ocean_current_direction",
                [None]
            )[0],

            "sea_surface_temperature": marine_hourly.get(
                "sea_surface_temperature",
                [None]
            )[0],

            "sea_level_height_msl": marine_hourly.get(
                "sea_level_height_msl",
                [None]
            )[0]
        }
    }
