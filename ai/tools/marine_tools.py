import json
import math
from pathlib import Path
from typing import Any

# Location of the PFZ JSON file
PFZ_FILE = Path(__file__).resolve().parents[2] / "data" / "pfz" / "pfz.json"


def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate distance between two geographic coordinates
    using the Haversine formula.
    """

    earth_radius_km = 6371.0

    lat1 = math.radians(latitude1)
    lat2 = math.radians(latitude2)

    delta_lat = math.radians(latitude2 - latitude1)
    delta_lon = math.radians(longitude2 - longitude1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius_km * c


def get_pfz_candidates(
    latitude: float,
    longitude: float,
    time: str,
    limit: int = 20
) -> dict:
    """
    Find the nearest PFZ candidates for a given location and time.

    Input:
        latitude  - source/user latitude
        longitude - source/user longitude
        time      - requested date/time
        limit     - maximum number of PFZ candidates

    Output:
        Dictionary containing PFZ candidates for AgentState.
    """

    # Load PFZ data
    with open(PFZ_FILE, "r", encoding="utf-8") as file:
        pfz_data = json.load(file)

    # Extract PFZ locations
    pfz_locations = pfz_data.get("pfz_locations", [])

    # Extract forecast dates
    forecast_validity = pfz_data.get("forecast_validity", {})

    valid_from = forecast_validity.get("from")
    valid_to = forecast_validity.get("to")

    # Extract date from input time
    requested_date = time[:10]

    # Convert forecast dates to YYYY-MM-DD
    from datetime import datetime

    from_date = datetime.strptime(
        valid_from, "%d %b %Y"
    ).date()

    to_date = datetime.strptime(
        valid_to, "%d %b %Y"
    ).date()

    requested = datetime.strptime(
        requested_date, "%Y-%m-%d"
    ).date()

    # Check whether requested date is within forecast validity
    if not (from_date <= requested <= to_date):
        return {
            "state": "pfz_candidates",
            "pfz_candidates": [],
            "message": (
                f"No PFZ forecast available for {requested_date}. "
                f"Available forecast: {valid_from} to {valid_to}."
            )
        }

    # Calculate distance for every PFZ
    candidates = []

    for index, pfz in enumerate(pfz_locations, start=1):

        pfz_latitude = pfz.get("latitude")
        pfz_longitude = pfz.get("longitude")

        if pfz_latitude is None or pfz_longitude is None:
            continue

        distance = calculate_distance_km(
            latitude,
            longitude,
            pfz_latitude,
            pfz_longitude
        )

        candidate = {
            "id": f"PFZ{index:02d}",
            "latitude": pfz_latitude,
            "longitude": pfz_longitude,
            "distance_from_source_km": round(distance, 2),
            "coastal_reference": pfz.get("coastal_reference"),
            "direction": pfz.get("direction"),
            "bearing_deg": pfz.get("bearing_deg"),
            "pfz_distance_km": pfz.get("distance_km"),
            "depth_m": pfz.get("depth_m"),
            "forecast_validity": forecast_validity,
            "source": pfz_data.get("source")
        }

        candidates.append(candidate)

    # Sort by distance from user's location
    candidates.sort(
        key=lambda item: item["distance_from_source_km"]
    )

    # Keep only Top 20
    candidates = candidates[:limit]

    return {
        "state": "pfz_candidates",
        "pfz_candidates": candidates,
        "count": len(candidates),
        "source": pfz_data.get("source"),
        "forecast_validity": forecast_validity
    }
    def select_pfz(
    pfz_candidates: list[dict[str, Any]],
    pfz_id: str
) -> dict | None:
    """
    Select a specific PFZ from the list of PFZ candidates.

    Input:
        pfz_candidates - list of PFZ candidate dictionaries
        pfz_id         - PFZ ID such as PFZ01, PFZ11, etc.

    Output:
        Selected PFZ dictionary, or None if not found.
    """

    pfz_id = pfz_id.upper().strip()

    for pfz in pfz_candidates:
        if pfz.get("id") == pfz_id:
            return pfz

    return None