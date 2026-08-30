import requests
import json
from datetime import datetime

MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


def get_marine_data(
    latitude: float,
    longitude: float,
    time: str
) -> dict:
    params = {
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

    response = requests.get(
        MARINE_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    hourly = data.get("hourly", {})

    return {
        "time": hourly.get("time", [None])[0],

        "wave_height": hourly.get(
            "wave_height", [None]
        )[0],

        "wave_direction": hourly.get(
            "wave_direction", [None]
        )[0],

        "wave_period": hourly.get(
            "wave_period", [None]
        )[0],

        "swell_wave_height": hourly.get(
            "swell_wave_height", [None]
        )[0],

        "swell_wave_direction": hourly.get(
            "swell_wave_direction", [None]
        )[0],

        "swell_wave_period": hourly.get(
            "swell_wave_period", [None]
        )[0],

        "ocean_current_velocity": hourly.get(
            "ocean_current_velocity", [None]
        )[0],

        "ocean_current_direction": hourly.get(
            "ocean_current_direction", [None]
        )[0],

        "sea_surface_temperature": hourly.get(
            "sea_surface_temperature", [None]
        )[0],

        "sea_level_height_msl": hourly.get(
            "sea_level_height_msl", [None]
        )[0]
    }
INCOIS_API_URL = (
    "https://sarat.incois.gov.in/"
    "incoismobileappdata/rest/incois/hwassalatestdata"
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


def normalize(value):
    if value is None:
        return ""

    value = str(value).strip().upper()

    suffixes = [
        " MUNICIPAL CORPORATION",
        " MUNICIPALITY",
        " CORPORATION",
        " CITY CORPORATION"
    ]

    for suffix in suffixes:
        if value.endswith(suffix):
            value = value[:-len(suffix)].strip()
            break

    return " ".join(value.split())


def parse_json_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return parsed

            if isinstance(parsed, dict):
                return [parsed]

        except json.JSONDecodeError:
            return []

    return []


def get_location(latitude, longitude):

    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "zoom": 10,
        "addressdetails": 1
    }

    headers = {
        "User-Agent": "ORCA-Marine-Risk-System/1.0"
    }

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    address = data.get("address", {})

    candidates = [
        address.get("city"),
        address.get("municipality"),
        address.get("town"),
        address.get("village"),
        address.get("county"),
        address.get("state_district"),
        address.get("city_district")
    ]

    candidates = [
        value for value in candidates
        if value
    ]

    unique_candidates = []

    for value in candidates:
        if value not in unique_candidates:
            unique_candidates.append(value)

    district = (
        address.get("city")
        or address.get("municipality")
        or address.get("town")
        or address.get("county")
        or address.get("state_district")
    )

    return {
        "district": district,
        "state": address.get("state"),
        "candidates": unique_candidates,
        "display_name": data.get("display_name")
    }


def find_matching_district(location, alerts):

    candidates = location.get("candidates", [])

    state = normalize(location.get("state"))

    normalized_candidates = [
        normalize(candidate)
        for candidate in candidates
    ]

    for alert in alerts:

        if normalize(alert.get("STATE")) != state:
            continue

        incois_districts = [
            normalize(district)
            for district in str(
                alert.get("District", "")
            ).split(",")
        ]

        for candidate in normalized_candidates:

            if candidate in incois_districts:
                return candidate

    return None


def get_latest_date(alerts):

    dates = []

    for alert in alerts:

        date_value = alert.get("Issue Date")

        if not date_value:
            continue

        try:
            date_obj = datetime.strptime(
                date_value,
                "%d-%m-%Y"
            )

            dates.append(date_obj)

        except ValueError:
            continue

    if not dates:
        return None

    return max(dates).strftime("%Y%m%d")


def get_marine_warning(latitude: float, longitude: float) -> dict:

    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    location = get_location(
        latitude,
        longitude
    )

    response = requests.get(
        INCOIS_API_URL,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    hwa_list = parse_json_list(
        data.get("HWAJson")
    )

    ssa_list = parse_json_list(
        data.get("SSAJson")
    )

    hwa_district = find_matching_district(
        location,
        hwa_list
    )

    ssa_district = find_matching_district(
        location,
        ssa_list
    )

    incois_district = (
        hwa_district
        or ssa_district
    )

    high_wave_warning = None

    if hwa_district:

        for alert in hwa_list:

            districts = [
                normalize(d)
                for d in str(
                    alert.get("District", "")
                ).split(",")
            ]

            if (
                hwa_district in districts
                and normalize(alert.get("STATE"))
                == normalize(location.get("state"))
            ):
                high_wave_warning = alert
                break

    swell_surge_warning = None

    if ssa_district:

        for alert in ssa_list:

            districts = [
                normalize(d)
                for d in str(
                    alert.get("District", "")
                ).split(",")
            ]

            if (
                ssa_district in districts
                and normalize(alert.get("STATE"))
                == normalize(location.get("state"))
            ):
                swell_surge_warning = alert
                break

    return {
        "latitude": latitude,
        "longitude": longitude,
        "location_name": location.get("display_name"),
        "district": location.get("district"),
        "state": location.get("state"),
        "incois_district": incois_district,
        "warning": bool(
            high_wave_warning
            or swell_surge_warning
        ),
        "high_wave_warning": high_wave_warning,
        "swell_surge_warning": swell_surge_warning,
        "latest_high_wave_date": get_latest_date(hwa_list),
        "latest_swell_surge_date": get_latest_date(ssa_list)
    }
