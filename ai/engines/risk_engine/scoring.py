from typing import Optional


# ============================================================
# WEATHER INDIVIDUAL FACTOR SCORING
# ============================================================

def score_wind_speed(wind_speed: float) -> int:

    if wind_speed <= 10:
        return 0
    elif wind_speed <= 20:
        return 1
    elif wind_speed <= 30:
        return 2
    else:
        return 3


def score_wind_direction(wind_direction: float) -> int:
    # Direction alone does not indicate risk.
    return 0


def score_visibility(visibility: float) -> int:

    if visibility >= 10:
        return 0
    elif visibility >= 5:
        return 1
    elif visibility >= 1:
        return 2
    else:
        return 3


def score_precipitation(precipitation: float) -> int:

    if precipitation <= 10:
        return 0
    elif precipitation <= 30:
        return 1
    elif precipitation <= 60:
        return 2
    else:
        return 3


def score_lightning(lightning: bool) -> int:

    if lightning:
        return 3

    return 0


def score_weather_condition(condition: str) -> int:

    if not condition:
        return 0

    condition = condition.strip().lower()

    if condition in {
        "clear",
        "sunny",
        "fair"
    }:
        return 0

    elif condition in {
        "cloudy",
        "partly cloudy",
        "overcast"
    }:
        return 1

    elif condition in {
        "rain",
        "light rain",
        "drizzle"
    }:
        return 2

    elif condition in {
        "heavy rain",
        "storm",
        "thunderstorm"
    }:
        return 3

    return 0


def score_weather_wave_height(wave_height: float) -> int:

    if wave_height <= 0.5:
        return 0
    elif wave_height <= 2.5:
        return 1
    elif wave_height <= 6.0:
        return 2
    else:
        return 3


def score_weather(weather: dict) -> dict:

    return {

        "wind_speed": score_wind_speed(
            weather["wind_speed"]
        ),

        "wind_direction": score_wind_direction(
            weather["wind_direction"]
        ),

        "wave_height": score_weather_wave_height(
            weather["wave_height"]
        ),

        "visibility": score_visibility(
            weather["visibility"]
        ),

        "precipitation": score_precipitation(
            weather["precipitation"]
        ),

        "lightning": score_lightning(
            weather["lightning"]
        ),

        "condition": score_weather_condition(
            weather["condition"]
        )
    }


# ============================================================
# MARINE INDIVIDUAL FACTOR SCORING
# ============================================================

def score_wave_height(wave_height: float) -> int:

    if wave_height <= 0.5:
        return 0
    elif wave_height <= 2.5:
        return 1
    elif wave_height <= 6.0:
        return 2
    else:
        return 3


def score_wave_period(wave_period: float) -> int:

    if wave_period < 8:
        return 0
    elif wave_period < 14:
        return 1
    else:
        return 2


def score_wave_direction(wave_direction: float) -> int:

    # Direction alone does not indicate risk.
    return 0


def score_swell_height(swell_height: float) -> int:

    if swell_height <= 2.0:
        return 0
    elif swell_height <= 4.0:
        return 2
    else:
        return 3


def score_swell_period(swell_period: float) -> int:

    if swell_period < 8:
        return 0
    elif swell_period < 14:
        return 1
    else:
        return 2


def score_swell_direction(swell_direction: float) -> int:

    # Direction alone does not indicate risk.
    return 0


def score_ocean_current_velocity(velocity: float) -> int:

    if velocity <= 2.0:
        return 0
    elif velocity <= 5.0:
        return 1
    elif velocity <= 8.0:
        return 2
    else:
        return 3


def score_ocean_current_direction(direction: float) -> int:

    # Direction alone does not indicate risk.
    return 0


def score_sea_surface_temperature(
    temperature: float
) -> int:

    # Supporting information only.
    return 0


def score_sea_level_height(
    sea_level_height: float
) -> int:

    # Supporting information only.
    return 0


def score_marine_warning(
    warning: Optional[str]
) -> int:

    if not warning:
        return 0

    warning = warning.strip().upper()

    if warning in {
        "NONE",
        "NO WARNING",
        "CLEAR"
    }:
        return 0

    elif warning in {
        "ADVISORY",
        "CAUTION"
    }:
        return 1

    elif warning == "WATCH":
        return 2

    elif warning in {
        "WARNING",
        "GALE",
        "STORM",
        "SEVERE",
        "HURRICANE_FORCE"
    }:
        return 3

    return 0


def score_marine(marine: dict) -> dict:

    return {

        "wave_height": score_wave_height(
            marine["wave_height"]
        ),

        "wave_period": score_wave_period(
            marine["wave_period"]
        ),

        "wave_direction": score_wave_direction(
            marine["wave_direction"]
        ),

        "swell_wave_height": score_swell_height(
            marine["swell_wave_height"]
        ),

        "swell_wave_period": score_swell_period(
            marine["swell_wave_period"]
        ),

        "swell_wave_direction": score_swell_direction(
            marine["swell_wave_direction"]
        ),

        "ocean_current_velocity": score_ocean_current_velocity(
            marine["ocean_current_velocity"]
        ),

        "ocean_current_direction": score_ocean_current_direction(
            marine["ocean_current_direction"]
        ),

        "sea_surface_temperature": score_sea_surface_temperature(
            marine["sea_surface_temperature"]
        ),

        "sea_level_height_msl": score_sea_level_height(
            marine["sea_level_height_msl"]
        ),

        "marine_warning": score_marine_warning(
            marine.get("marine_warning")
        )
    }


# ============================================================
# GEOGRAPHICAL INDIVIDUAL FACTOR SCORING
# ============================================================

def score_restricted_area(restricted_area: bool) -> int:

    if restricted_area:
        return 3

    return 0


def score_protected_area(protected_area: bool) -> int:

    if protected_area:
        return 3

    return 0


def score_geography(geo: dict) -> dict:

    return {

        "latitude": 0,

        "longitude": 0,

        "restricted_area": score_restricted_area(
            geo["restricted_area"]
        ),

        "protected_area": score_protected_area(
            geo["protected_area"]
        )
    }


# ============================================================
# FACTOR CLASSIFICATION
# ============================================================

CRITICAL_FACTORS = {

    "marine": {
        "marine_warning"
    },

    "weather": {
        "lightning"
    },

    "geo": {
        "restricted_area"
    }
}


PRIMARY_HAZARD_FACTORS = {

    "weather": {
        "wind_speed",
        "visibility",
        "precipitation",
        "condition",
        "wave_height"
    },

    "marine": {
        "wave_height",
        "wave_period",
        "swell_wave_height",
        "swell_wave_period",
        "ocean_current_velocity"
    },

    "geo": {
        "protected_area"
    }
}


SUPPORTING_FACTORS = {

    "weather": {
        "wind_direction"
    },

    "marine": {
        "wave_direction",
        "swell_wave_direction",
        "ocean_current_direction",
        "sea_surface_temperature",
        "sea_level_height_msl"
    },

    "geo": {
        "latitude",
        "longitude"
    }
}


# ============================================================
# DOMAIN RISK CALCULATION
# ============================================================

def calculate_domain_score(
    factor_scores: dict,
    domain: str
) -> float:

    critical_scores = [
        factor_scores[factor]
        for factor in CRITICAL_FACTORS.get(domain, set())
        if factor in factor_scores
    ]

    primary_scores = [
        factor_scores[factor]
        for factor in PRIMARY_HAZARD_FACTORS.get(domain, set())
        if factor in factor_scores
    ]

    # --------------------------------------------------------
    # Critical factor handling
    # --------------------------------------------------------

    critical_score = max(
        critical_scores,
        default=0
    )

    # --------------------------------------------------------
    # Primary hazard calculation
    # --------------------------------------------------------

    primary_hazards = [
        score
        for score in primary_scores
        if score > 0
    ]

    if primary_hazards:

        highest_primary = max(primary_hazards)

        additional_hazards = len(
            primary_hazards
        ) - 1

        primary_score = (
            highest_primary * 20
            + additional_hazards * 5
        )

    else:

        primary_score = 0

    # --------------------------------------------------------
    # Critical factor escalation
    # --------------------------------------------------------

    if critical_score == 3:

        domain_score = max(
            primary_score,
            80
        )

    elif critical_score == 2:

        domain_score = max(
            primary_score,
            60
        )

    elif critical_score == 1:

        domain_score = max(
            primary_score,
            30
        )

    else:

        domain_score = primary_score

    return min(
        float(domain_score),
        100.0
    )


# ============================================================
# FINAL RISK CALCULATION
# ============================================================

def calculate_final_risk_score(
    weather_scores: dict,
    marine_scores: dict,
    geo_scores: dict
) -> dict:

    weather_score = calculate_domain_score(
        weather_scores,
        "weather"
    )

    marine_score = calculate_domain_score(
        marine_scores,
        "marine"
    )

    geo_score = calculate_domain_score(
        geo_scores,
        "geo"
    )

    domain_scores = {

        "weather_score": weather_score,

        "marine_score": marine_score,

        "geo_score": geo_score
    }

    # --------------------------------------------------------
    # Identify strongest domain
    # --------------------------------------------------------

    highest_domain_score = max(
        domain_scores.values()
    )

    # --------------------------------------------------------
    # Multi-hazard escalation
    # --------------------------------------------------------

    elevated_domains = sum(
        1
        for score in domain_scores.values()
        if score >= 40
    )

    final_score = highest_domain_score

    if elevated_domains >= 2:
        final_score += 10

    if elevated_domains == 3:
        final_score += 10

    # --------------------------------------------------------
    # Critical-factor override
    # --------------------------------------------------------

    critical_marine = marine_scores.get(
        "marine_warning",
        0
    )

    critical_lightning = weather_scores.get(
        "lightning",
        0
    )

    restricted_area = geo_scores.get(
        "restricted_area",
        0
    )

    critical_score = max(
        critical_marine,
        critical_lightning,
        restricted_area
    )

    if critical_score == 3:

        final_score = max(
            final_score,
            80
        )

    elif critical_score == 2:

        final_score = max(
            final_score,
            60
        )

    elif critical_score == 1:

        final_score = max(
            final_score,
            30
        )

    return {
        "weather_score": weather_score,
        "marine_score": marine_score,
        "geo_score": geo_score,
        "risk_score": min(
            float(final_score),
            100.0
        )
    }