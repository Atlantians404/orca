"""
Individual risk-factor scoring for ORCA Risk Engine.

Normalized ORCA score:
    0 = Normal
    1 = Caution
    2 = High
    3 = Severe

The score is an ORCA normalized engineering representation.
The underlying bands are based on established
meteorological/marine reference classifications.
"""


# =========================================================
# WEATHER FACTOR SCORING
# =========================================================

def score_wind_speed(wind_speed: float) -> int:
    """
    Wind speed is provided in km/h.

    Normalized from established Beaufort wind-force bands.
    """

    if wind_speed < 20:
        return 0
    elif wind_speed < 39:
        return 1
    elif wind_speed < 62:
        return 2
    else:
        return 3


def score_wind_gust(wind_gust: float) -> int:
    """
    Wind gust is provided in km/h.

    Normalized severity bands.
    """

    if wind_gust < 39:
        return 0
    elif wind_gust < 62:
        return 1
    elif wind_gust < 88:
        return 2
    else:
        return 3


def score_visibility(visibility: float) -> int:
    """
    Visibility is provided in metres.
    """

    if visibility > 5000:
        return 0
    elif visibility >= 1852:
        return 1
    elif visibility >= 1000:
        return 2
    else:
        return 3


def score_wind_direction(wind_direction: float) -> int:
    """
    Wind direction alone does not indicate risk.

    It will be used later for contextual/directional
    interaction analysis.
    """

    return 0


def score_temperature(temperature: float) -> int:
    """
    No universal standalone marine-risk threshold is
    applied to temperature at this stage.
    """

    return 0


def score_precipitation(precipitation: float) -> int:
    """
    Precipitation scoring is pending the provider's
    accumulation-period specification.
    """

    return 0


def score_weather_code(weather_code: int) -> int:
    """
    WMO weather code is categorical, not a numerical
    risk score.

    The code is mapped into ORCA's normalized severity.
    """

    if 0 <= weather_code <= 3:
        return 0

    elif 4 <= weather_code <= 18:
        return 1

    elif 19 <= weather_code <= 49:
        return 2

    elif 50 <= weather_code <= 94:
        return 2

    elif 95 <= weather_code <= 99:
        return 3

    return 0


def score_thunderstorm(thunderstorm: bool) -> int:
    """
    Presence of thunderstorm is treated as a severe
    individual weather hazard.
    """

    return 3 if thunderstorm else 0


# =========================================================
# WEATHER OUTPUT
# =========================================================

def score_weather(weather: dict) -> dict:
    """
    Return ONLY individual weather-factor risk scores.

    Original input values are NOT returned.
    """

    return {
        "wind_speed": score_wind_speed(
            weather["wind_speed"]
        ),

        "wind_direction": score_wind_direction(
            weather["wind_direction"]
        ),

        "wind_gust": score_wind_gust(
            weather["wind_gust"]
        ),

        "visibility": score_visibility(
            weather["visibility"]
        ),

        "precipitation": score_precipitation(
            weather["precipitation"]
        ),

        "temperature": score_temperature(
            weather["temperature"]
        ),

        "weather_code": score_weather_code(
            weather["weather_code"]
        ),

        "thunderstorm": score_thunderstorm(
            weather["thunderstorm"]
        )
    }