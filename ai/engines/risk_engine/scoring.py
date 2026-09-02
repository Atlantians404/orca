"""
ORCA Risk Engine
Deterministic Expert Risk Scoring

Individual factor:
    0 = normal
    1 = low
    2 = moderate
    3 = high

Normalization:
    normalized_score = factor_score / 3

Domain:
    domain_score =
        SUM(normalized_factor * factor_weight * 100)

Overall:
    weighted combination of
    Weather + Marine + Geo

No ML is used.
"""


# ============================================================
# DOMAIN WEIGHTS
# ============================================================

DOMAIN_WEIGHTS = {

    "weather": 0.30,

    "marine": 0.50,

    "geo": 0.20
}


# ============================================================
# PRIMARY FACTOR WEIGHTS
# ============================================================
#
# These are the factors that directly contribute
# to the risk calculation.
#
# Supporting information such as direction,
# temperature etc. is validated but does not
# directly contribute to risk at this stage.
# ============================================================


WEATHER_WEIGHTS = {

    "wind_speed": 0.30,

    "wave_height": 0.20,

    "visibility": 0.20,

    "precipitation": 0.10,

    "lightning": 0.20
}


MARINE_WEIGHTS = {

    "wave_height": 0.30,

    "swell_wave_height": 0.20,

    "ocean_current_velocity": 0.15,

    "marine_warning": 0.35
}


GEO_WEIGHTS = {

    "restricted_area": 0.60,

    "protected_area": 0.40
}


# ============================================================
# MARINE WARNING SCORES
# ============================================================

MARINE_WARNING_SCORES = {

    "NONE": 0,

    "ADVISORY": 1,

    "WARNING": 2,

    "SEVERE": 3
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_score(score: int) -> float:

    return score / 3.0


# ============================================================
# WEATHER FACTOR SCORING
# ============================================================

def score_wind_speed(value: float) -> int:

    if value < 8:
        return 0

    elif value < 12:
        return 1

    elif value < 17:
        return 2

    else:
        return 3


def score_wave_height(value: float) -> int:

    if value < 1.0:
        return 0

    elif value < 2.0:
        return 1

    elif value < 3.0:
        return 2

    else:
        return 3


def score_visibility(value: float) -> int:

    if value >= 10:
        return 0

    elif value >= 5:
        return 1

    elif value >= 2:
        return 2

    else:
        return 3


def score_precipitation(value: float) -> int:

    if value < 20:
        return 0

    elif value < 50:
        return 1

    elif value < 80:
        return 2

    else:
        return 3


def score_lightning(value: bool) -> int:

    if value:

        return 3

    return 0


# ============================================================
# MARINE FACTOR SCORING
# ============================================================

def score_swell_wave_height(value: float) -> int:

    if value < 0.5:
        return 0

    elif value < 1.0:
        return 1

    elif value < 2.0:
        return 2

    else:
        return 3


def score_ocean_current_velocity(value: float) -> int:

    if value < 0.5:
        return 0

    elif value < 1.0:
        return 1

    elif value < 1.5:
        return 2

    else:
        return 3


def score_marine_warning(value: str) -> int:

    warning = str(
        value
    ).strip().upper()

    return MARINE_WARNING_SCORES.get(
        warning,
        0
    )


# ============================================================
# GEO FACTOR SCORING
# ============================================================

def score_restricted_area(value: bool) -> int:

    if value:

        return 3

    return 0


def score_protected_area(value: bool) -> int:

    if value:

        return 1

    return 0


# ============================================================
# GENERIC DOMAIN CALCULATION
# ============================================================

def calculate_domain_score(
    factor_scores: dict,
    weights: dict
) -> float:

    total_weight = sum(
        weights.values()
    )

    if abs(
        total_weight - 1.0
    ) > 0.0001:

        raise ValueError(
            "Factor weights must sum to 1.0"
        )

    domain_score = 0.0

    for factor, weight in weights.items():

        factor_score = factor_scores.get(
            factor,
            0
        )

        normalized = normalize_score(
            factor_score
        )

        domain_score += (
            normalized
            * weight
            * 100
        )

    return round(
        domain_score,
        2
    )


# ============================================================
# WEATHER DOMAIN
# ============================================================

def calculate_weather_score(weather):

    factor_scores = {

        "wind_speed":
            score_wind_speed(
                weather.wind_speed
            ),

        "wave_height":
            score_wave_height(
                weather.wave_height
            ),

        "visibility":
            score_visibility(
                weather.visibility
            ),

        "precipitation":
            score_precipitation(
                weather.precipitation
            ),

        "lightning":
            score_lightning(
                weather.lightning
            )
    }

    domain_score = calculate_domain_score(
        factor_scores,
        WEATHER_WEIGHTS
    )

    return (
        domain_score,
        factor_scores
    )


# ============================================================
# MARINE DOMAIN
# ============================================================

def calculate_marine_score(marine):

    factor_scores = {

        "wave_height":
            score_wave_height(
                marine.wave_height
            ),

        "swell_wave_height":
            score_swell_wave_height(
                marine.swell_wave_height
            ),

        "ocean_current_velocity":
            score_ocean_current_velocity(
                marine.ocean_current_velocity
            ),

        "marine_warning":
            score_marine_warning(
                marine.marine_warning
            )
    }

    domain_score = calculate_domain_score(
        factor_scores,
        MARINE_WEIGHTS
    )

    return (
        domain_score,
        factor_scores
    )


# ============================================================
# GEO DOMAIN
# ============================================================

def calculate_geo_score(geo):

    factor_scores = {

        "restricted_area":
            score_restricted_area(
                geo.restricted_area
            ),

        "protected_area":
            score_protected_area(
                geo.protected_area
            )
    }

    domain_score = calculate_domain_score(
        factor_scores,
        GEO_WEIGHTS
    )

    return (
        domain_score,
        factor_scores
    )


# ============================================================
# MULTI-HAZARD INTERACTION
# ============================================================

def calculate_interaction_score(
    weather_factors,
    marine_factors
):

    interaction = 0.0

    # High wind + high waves
    wind = normalize_score(
        weather_factors["wind_speed"]
    )

    wave = normalize_score(
        marine_factors["wave_height"]
    )

    interaction += (
        10.0
        * wind
        * wave
    )

    # Lightning + marine warning
    lightning = normalize_score(
        weather_factors["lightning"]
    )

    warning = normalize_score(
        marine_factors["marine_warning"]
    )

    interaction += (
        10.0
        * lightning
        * warning
    )

    return round(
        interaction,
        2
    )


# ============================================================
# CRITICAL CONDITIONS
# ============================================================

def calculate_critical_floor(
    weather_factors,
    marine_factors,
    geo
):

    critical_floor = 0.0

    # Restricted area
    if geo.restricted_area:

        critical_floor = max(
            critical_floor,
            100.0
        )

    # Severe marine warning
    if (
        marine_factors["marine_warning"]
        == 3
    ):

        critical_floor = max(
            critical_floor,
            80.0
        )

    # Extreme waves
    if (
        marine_factors["wave_height"]
        == 3
    ):

        critical_floor = max(
            critical_floor,
            70.0
        )

    # Lightning + high wind
    if (
        weather_factors["lightning"] == 3
        and
        weather_factors["wind_speed"] >= 2
    ):

        critical_floor = max(
            critical_floor,
            70.0
        )

    return critical_floor


# ============================================================
# OVERALL RISK
# ============================================================

def calculate_overall_risk(
    weather_score,
    marine_score,
    geo_score,
    weather_factors,
    marine_factors,
    geo
):

    # --------------------------------------------------------
    # Weighted domain score
    # --------------------------------------------------------

    base_score = (

        weather_score
        * DOMAIN_WEIGHTS["weather"]

        +

        marine_score
        * DOMAIN_WEIGHTS["marine"]

        +

        geo_score
        * DOMAIN_WEIGHTS["geo"]
    )

    # --------------------------------------------------------
    # Interaction
    # --------------------------------------------------------

    interaction_score = (
        calculate_interaction_score(
            weather_factors,
            marine_factors
        )
    )

    calculated_score = (
        base_score
        + interaction_score
    )

    # --------------------------------------------------------
    # Critical floor
    # --------------------------------------------------------

    critical_floor = (
        calculate_critical_floor(
            weather_factors,
            marine_factors,
            geo
        )
    )

    final_score = max(
        calculated_score,
        critical_floor
    )

    final_score = min(
        final_score,
        100.0
    )

    return round(
        final_score,
        2
    )


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(
    score: float
) -> str:

    if score < 30:

        return "LOW"

    elif score < 60:

        return "MEDIUM"

    elif score < 80:

        return "HIGH"

    else:

        return "CRITICAL"


# ============================================================
# COMPLETE SINGLE RECORD CALCULATION
# ============================================================

def calculate_risk(data):

    weather_score, weather_factors = (
        calculate_weather_score(
            data.weather
        )
    )

    marine_score, marine_factors = (
        calculate_marine_score(
            data.marine
        )
    )

    geo_score, geo_factors = (
        calculate_geo_score(
            data.geo
        )
    )

    risk_score = calculate_overall_risk(

        weather_score,

        marine_score,

        geo_score,

        weather_factors,

        marine_factors,

        data.geo
    )

    return {

        "weather_score":
            weather_score,

        "marine_score":
            marine_score,

        "geo_score":
            geo_score,

        "risk_score":
            risk_score,

        "risk_level":
            get_risk_level(
                risk_score
            )
    }