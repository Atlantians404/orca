import os
import math
from pathlib import Path
from typing import Any
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient


# Load .env from D:\ORCA\.env
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)


def get_mongodb_collection():
    """
    Connect to MongoDB and return the PFZ collection.
    """

    mongodb_uri = os.getenv("MONGODB_URI")

    if not mongodb_uri:
        raise ValueError(
            "MONGODB_URI not found in environment."
        )

    client = MongoClient(mongodb_uri)

    db = client["ORCA"]
    collection = db["pfz"]

    return collection


def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate distance between two geographic coordinates
    using the Haversine formula.

    Returns:
        Distance in kilometers.
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

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


def get_pfz_candidates(
    latitude: float,
    longitude: float,
    requested_date: str | None = None,
    radius_km: float | None = None,
    limit: int = 20
) -> dict[str, Any]:
    """
    Find PFZ candidates near a given location
    for the requested date.

    Parameters:
        latitude:
            Latitude of the user's current location.

        longitude:
            Longitude of the user's current location.

        requested_date:
            Date for which PFZ data is required.
            Format: YYYY-MM-DD

            If not provided, today's date is used.

        radius_km:
            Optional search radius in kilometers.

            Example:
                radius_km=10

            This returns only PFZs within 10 km
            of the user's location.

            If None, PFZs are searched without
            a radius restriction.

        limit:
            Maximum number of PFZ candidates to return.

    Returns:
        Dictionary containing PFZ candidates,
        distance information, source and metadata.
    """

    # ---------------------------------------------------------
    # Validate latitude and longitude
    # ---------------------------------------------------------

    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    # ---------------------------------------------------------
    # Validate radius
    # ---------------------------------------------------------

    if radius_km is not None and radius_km <= 0:
        raise ValueError(
            "radius_km must be greater than 0."
        )

    # ---------------------------------------------------------
    # Validate limit
    # ---------------------------------------------------------

    if limit <= 0:
        raise ValueError(
            "limit must be greater than 0."
        )

    # ---------------------------------------------------------
    # Use today's date if no date is provided
    # ---------------------------------------------------------

    if requested_date is None:
        requested_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    # ---------------------------------------------------------
    # Validate requested date
    # ---------------------------------------------------------

    try:
        requested = datetime.strptime(
            requested_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        raise ValueError(
            "requested_date must be in YYYY-MM-DD format."
        )

    # ---------------------------------------------------------
    # Connect to MongoDB
    # ---------------------------------------------------------

    collection = get_mongodb_collection()

    # ---------------------------------------------------------
    # Find PFZ advisory valid for requested date
    # ---------------------------------------------------------

    document = None

    for pfz_document in collection.find({}):

        validity = pfz_document.get(
            "forecast_validity",
            {}
        )

        valid_from = validity.get("from")
        valid_to = validity.get("to")

        if not valid_from or not valid_to:
            continue

        try:
            start_date = datetime.strptime(
                valid_from,
                "%d %b %Y"
            ).date()

            end_date = datetime.strptime(
                valid_to,
                "%d %b %Y"
            ).date()

        except ValueError:
            continue

        if start_date <= requested <= end_date:
            document = pfz_document
            break

    # ---------------------------------------------------------
    # No PFZ advisory for requested date
    # ---------------------------------------------------------

    if not document:
        return {
            "state": "pfz_candidates",
            "pfz_candidates": [],
            "count": 0,
            "requested_date": requested_date,
            "radius_km": radius_km,
            "user_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "message": (
                f"No PFZ advisory available for "
                f"{requested_date}."
            )
        }

    # ---------------------------------------------------------
    # Get PFZ locations
    # ---------------------------------------------------------

    pfz_locations = document.get(
        "pfz_locations",
        []
    )

    candidates = []

    # ---------------------------------------------------------
    # Calculate distance and filter PFZs
    # ---------------------------------------------------------

    for index, pfz in enumerate(
        pfz_locations,
        start=1
    ):

        pfz_latitude = pfz.get("latitude")
        pfz_longitude = pfz.get("longitude")

        # Skip PFZ entries without coordinates
        if (
            pfz_latitude is None
            or pfz_longitude is None
        ):
            continue

        # Calculate distance from user's location
        distance = calculate_distance_km(
            latitude,
            longitude,
            pfz_latitude,
            pfz_longitude
        )

        # -----------------------------------------------------
        # Radius filter
        # -----------------------------------------------------

        if (
            radius_km is not None
            and distance > radius_km
        ):
            continue

        candidate = {
            "id": f"PFZ{index:02d}",
            "latitude": pfz_latitude,
            "longitude": pfz_longitude,
            "distance_from_source_km": round(
                distance,
                2
            ),
            "coastal_reference": pfz.get(
                "coastal_reference"
            ),
            "direction": pfz.get(
                "direction"
            ),
            "bearing_deg": pfz.get(
                "bearing_deg"
            ),
            "pfz_distance_km": pfz.get(
                "distance_km"
            ),
            "depth_m": pfz.get(
                "depth_m"
            ),
            "source": document.get(
                "source"
            )
        }

        candidates.append(candidate)

    # ---------------------------------------------------------
    # Sort nearest PFZ first
    # ---------------------------------------------------------

    candidates.sort(
        key=lambda item:
        item["distance_from_source_km"]
    )

    # ---------------------------------------------------------
    # Apply maximum result limit
    # ---------------------------------------------------------

    candidates = candidates[:limit]

    # ---------------------------------------------------------
    # No PFZ found within requested radius
    # ---------------------------------------------------------

    if not candidates:

        if radius_km is not None:
            message = (
                f"No PFZ found within "
                f"{radius_km} km of the given location "
                f"for {requested_date}."
            )
        else:
            message = (
                f"No PFZ locations available for "
                f"{requested_date}."
            )

        return {
            "state": "pfz_candidates",
            "pfz_candidates": [],
            "count": 0,
            "source": document.get("source"),
            "sector": document.get("sector"),
            "requested_date": requested_date,
            "radius_km": radius_km,
            "user_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "forecast_validity": document.get(
                "forecast_validity"
            ),
            "message": message
        }

    # ---------------------------------------------------------
    # Return PFZ results
    # ---------------------------------------------------------

    return {
        "state": "pfz_candidates",
        "pfz_candidates": candidates,
        "count": len(candidates),
        "source": document.get("source"),
        "sector": document.get("sector"),
        "requested_date": requested_date,
        "radius_km": radius_km,
        "user_location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "forecast_validity": document.get(
            "forecast_validity"
        )
    }


def select_pfz(
    pfz_candidates: list[dict[str, Any]],
    pfz_id: str
) -> dict[str, Any] | None:
    """
    Select a specific PFZ from PFZ candidates.

    Example:
        select_pfz(candidates, "PFZ01")
    """

    pfz_id = pfz_id.upper().strip()

    for pfz in pfz_candidates:

        if pfz.get("id") == pfz_id:
            return pfz

    return None