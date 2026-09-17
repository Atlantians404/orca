import asyncio
import time

import httpx


WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MAX_RETRIES = 2
DEFAULT_RETRY_DELAY = 3

# Cache weather results for 10 minutes.
CACHE_TTL = 60 * 10


_weather_cache: dict[
    tuple[float, float, str | None],
    tuple[float, dict]
] = {}


# ---------------------------------------------------------
# Weather helpers
# ---------------------------------------------------------

def weather_condition_from_code(weather_code):

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
        99: "Thunderstorm with heavy hail",
    }

    return conditions.get(
        weather_code,
        "Unknown"
    )


def is_thunderstorm(weather_code):

    return weather_code in [95, 96, 99]


# ---------------------------------------------------------
# Time helper
# ---------------------------------------------------------

def normalize_weather_time(value):
    """
    Open-Meteo with timezone=auto should receive
    local time without a trailing Z.

    Example:

        2026-09-17T06:00:00Z
        ->
        2026-09-17T06:00

        2026-09-17T06:00:00
        ->
        2026-09-17T06:00
    """

    if value is None:
        return None

    value = str(value).strip()

    # Remove UTC suffix.
    value = value.replace("Z", "")

    # Remove timezone offset if present.
    # Example:
    # 2026-09-17T06:00:00+00:00
    if "+" in value:

        value = value.split("+")[0]

    # Keep only YYYY-MM-DDTHH:MM
    if "T" in value:

        date_part, time_part = value.split(
            "T",
            1
        )

        time_part = time_part[:5]

        return f"{date_part}T{time_part}"

    return value


# ---------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------

def _cache_key(
    latitude: float,
    longitude: float,
    weather_time: str | None
):

    return (
        round(float(latitude), 4),
        round(float(longitude), 4),
        weather_time
    )


def _get_cached_weather(key):

    cached = _weather_cache.get(key)

    if cached is None:
        return None

    cached_time, data = cached

    if time.time() - cached_time > CACHE_TTL:

        _weather_cache.pop(
            key,
            None
        )

        return None

    return data


def _set_cached_weather(
    key,
    data
):

    _weather_cache[key] = (
        time.time(),
        data
    )


# ---------------------------------------------------------
# Main Open-Meteo request
# ---------------------------------------------------------

async def get_open_meteo_data(
    latitude: float,
    longitude: float,
    weather_time: str | None = None
) -> dict:

    # -----------------------------------------------------
    # Normalize time
    # -----------------------------------------------------

    normalized_time = normalize_weather_time(
        weather_time
    )

    key = _cache_key(
        latitude,
        longitude,
        normalized_time
    )

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    cached = _get_cached_weather(key)

    if cached is not None:

        print(
            f"[OPEN-METEO] CACHE HIT "
            f"{latitude}, {longitude}, "
            f"{normalized_time}"
        )

        return cached

    print(
        f"[OPEN-METEO] API REQUEST "
        f"{latitude}, {longitude}, "
        f"{normalized_time}"
    )

    # -----------------------------------------------------
    # PARAMETERS
    # -----------------------------------------------------

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
            "weather_code",
        ],

        "timezone": "auto",
    }

    # -----------------------------------------------------
    # IMPORTANT
    # -----------------------------------------------------
    # Use normalized local time.
    #
    # DO NOT send:
    #
    # 2026-09-17T00:00:00Z
    #
    # Send:
    #
    # 2026-09-17T00:00
    #
    # -----------------------------------------------------

    if normalized_time is not None:

        weather_params[
            "start_hour"
        ] = normalized_time

        weather_params[
            "end_hour"
        ] = normalized_time

    # -----------------------------------------------------
    # HTTP CLIENT
    # -----------------------------------------------------

    async with httpx.AsyncClient(
        timeout=15
    ) as client:

        for attempt in range(
            MAX_RETRIES
        ):

            try:

                response = await client.get(
                    WEATHER_URL,
                    params=weather_params
                )

                # -------------------------------------------------
                # RATE LIMIT
                # -------------------------------------------------

                if response.status_code == 429:

                    if attempt == MAX_RETRIES - 1:

                        print(
                            "[OPEN-METEO] "
                            "429 - retries exhausted"
                        )

                        return {}

                    retry_after = (
                        response.headers.get(
                            "Retry-After"
                        )
                    )

                    if retry_after:

                        try:

                            wait_time = float(
                                retry_after
                            )

                        except ValueError:

                            wait_time = (
                                DEFAULT_RETRY_DELAY
                            )

                    else:

                        wait_time = min(
                            DEFAULT_RETRY_DELAY
                            * (2 ** attempt),
                            15
                        )

                    print(
                        f"[OPEN-METEO] 429 - "
                        f"waiting {wait_time}s "
                        f"(attempt "
                        f"{attempt + 1}/"
                        f"{MAX_RETRIES})"
                    )

                    await asyncio.sleep(
                        wait_time
                    )

                    continue

                # -------------------------------------------------
                # OTHER HTTP ERRORS
                # -------------------------------------------------

                if response.status_code != 200:

                    print(
                        f"[OPEN-METEO] "
                        f"HTTP {response.status_code}"
                    )

                    print(
                        response.text[:500]
                    )

                    return {}

                # -------------------------------------------------
                # SUCCESS
                # -------------------------------------------------

                data = response.json()

                hourly = data.get(
                    "hourly",
                    {}
                )

                # -------------------------------------------------
                # Extract weather code
                # -------------------------------------------------

                weather_code = hourly.get(
                    "weather_code",
                    [None]
                )[0]

                # -------------------------------------------------
                # SAME WEATHER RESPONSE FORMAT
                # -------------------------------------------------

                result = {

                    "latitude": latitude,

                    "longitude": longitude,

                    "time": hourly.get(
                        "time",
                        [normalized_time]
                    )[0],

                    "timezone": data.get(
                        "timezone"
                    ),

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

                    "weather_condition":
                        weather_condition_from_code(
                            weather_code
                        ),

                    "thunderstorm":
                        is_thunderstorm(
                            weather_code
                        ),
                }

                # -------------------------------------------------
                # CACHE
                # -------------------------------------------------

                _set_cached_weather(
                    key,
                    result
                )

                print(
                    f"[OPEN-METEO] SUCCESS "
                    f"{latitude}, "
                    f"{longitude}, "
                    f"{normalized_time}"
                )

                return result

            except httpx.RequestError as exc:

                if attempt == MAX_RETRIES - 1:

                    print(
                        f"[OPEN-METEO] "
                        f"Network error: {exc}"
                    )

                    return {}

                wait_time = min(
                    DEFAULT_RETRY_DELAY
                    * (2 ** attempt),
                    15
                )

                print(
                    f"[OPEN-METEO] "
                    f"Network error: {exc}. "
                    f"Retrying in {wait_time}s"
                )

                await asyncio.sleep(
                    wait_time
                )

    return {}


# ---------------------------------------------------------
# Individual helpers
# ---------------------------------------------------------

async def get_temperature(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "temperature"
    )


async def get_wind_speed(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "wind_speed"
    )


async def get_wind_direction(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "wind_direction"
    )


async def get_wind_gust(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "wind_gust"
    )


async def get_visibility(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "visibility"
    )


async def get_precipitation(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "precipitation"
    )


async def get_weather_code(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "weather_code"
    )


async def get_weather_condition(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "weather_condition"
    )


async def get_thunderstorm(
    latitude,
    longitude,
    time
):

    data = await get_open_meteo_data(
        latitude,
        longitude,
        time
    )

    return data.get(
        "thunderstorm"
    )