import os
import math
from pathlib import Path
from typing import Any
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# MongoDB connection
# ---------------------------------------------------------

def get_mongodb_collection():
    """
    Connect to MongoDB Atlas and return the PFZ collection.
    """

    mongodb_uri = os.getenv("MONGODB_URI")

    if not mongodb_uri:
        raise ValueError(
            "MONGODB_URI not found in .env file."
        )

    client = MongoClient(mongodb_uri)

    db = client["ORCA"]
    collection = db["pfz"]

    return collection


# ---------------------------------------------------------
# Distance calculation
# ---------------------------------------------------------

def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate the distance between two latitude/longitude
    coordinates using the Haversine formula.

    Returns:
        Distance in kilometres.
    """

    earth_radius_km = 6371.0

    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)

    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

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


# ---------------------------------------------------------
# Get currently valid PFZ advisory
# ---------------------------------------------------------

def get_current_pfz_advisory(collection):
    """
    Find the PFZ advisory that is currently valid.

    The function automatically checks today's date against
    the advisory's forecast validity period.
    """

    today = datetime.now().date()

    advisories = collection.find({})

    for advisory in advisories:

        forecast_validity = advisory.get(
            "forecast_validity",
            {}
        )

        start_date_text = forecast_validity.get("from")
        end_date_text = forecast_validity.get("to")

        if not start_date_text or not end_date_text:
            continue

        try:
            start_date = datetime.strptime(
                start_date_text,
                "%d %b %Y"
            ).date()

            end_date = datetime.strptime(
                end_date_text,
                "%d %b %Y"
            ).date()

        except ValueError:
            continue

        if start_date <= today <= end_date:
            return advisory

    return None


# ---------------------------------------------------------
# Get nearest PFZ zones
# ---------------------------------------------------------

def get_pfz_candidates(
    latitude: float,
    longitude: float,
    radius_km: float | None = None,
    number_of_zones: int = 20
):
    """
    Find the nearest PFZ zones to a given latitude/longitude.

    Parameters:
        latitude: User/source latitude.
        longitude: User/source longitude.
        radius_km: Optional search radius in kilometres.
        number_of_zones: Maximum number of PFZ zones to return.

    Returns:
        Dictionary containing the nearest PFZ zones.
    """

    # Validate latitude
    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    # Validate longitude
    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    # Validate radius
    if radius_km is not None and radius_km <= 0:
        raise ValueError(
            "Radius must be greater than 0 km."
        )

    # Validate number of zones
    if number_of_zones <= 0:
        raise ValueError(
            "Number of zones must be greater than 0."
        )

    # Get MongoDB collection
    collection = get_mongodb_collection()

    # Get currently valid PFZ advisory
    advisory = get_current_pfz_advisory(collection)

    # No current advisory available
    if not advisory:
        return {
            "state": "pfz_candidates",
            "source_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "radius_km": radius_km,
            "requested_number_of_zones": number_of_zones,
            "returned_number_of_zones": 0,
            "pfz_zones": {},
            "count": 0,
            "message": (
                "No currently valid PFZ advisory is available."
            )
        }

    # PFZ locations are stored in "pfz_locations"
    locations = advisory.get(
        "pfz_locations",
        []
    )

    candidates = []

    # Calculate distance from user's location
    for pfz in locations:

        try:
            pfz_latitude = float(
                pfz["latitude"]
            )

            pfz_longitude = float(
                pfz["longitude"]
            )

        except (KeyError, TypeError, ValueError):
            continue

        distance = calculate_distance_km(
            latitude,
            longitude,
            pfz_latitude,
            pfz_longitude
        )

        # If radius is provided,
        # ignore PFZs outside the radius
        if (
            radius_km is not None
            and distance > radius_km
        ):
            continue

        candidates.append({
            "name": pfz.get(
                "coastal_reference",
                "Unknown PFZ"
            ),
            "latitude": pfz_latitude,
            "longitude": pfz_longitude,
            "distance_from_source_km": round(
                distance,
                2
            )
        })

    # Sort nearest → farthest
    candidates.sort(
        key=lambda pfz:
        pfz["distance_from_source_km"]
    )

    # Take nearest requested number of zones
    candidates = candidates[
        :number_of_zones
    ]

    # Convert to required dictionary format
    pfz_zones = {}

    for index, pfz in enumerate(
        candidates,
        start=1
    ):
        pfz_zones[
            f"pfz{index}"
        ] = pfz

    return {
        "state": "pfz_candidates",
        "source_location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "radius_km": radius_km,
        "requested_number_of_zones": number_of_zones,
        "returned_number_of_zones": len(
            pfz_zones
        ),
        "pfz_zones": pfz_zones,
        "count": len(pfz_zones),
        "message": (
            "PFZ candidates retrieved successfully."
            if pfz_zones
            else "No PFZ zones found."
        )
    }


# ---------------------------------------------------------
# Select one PFZ
# ---------------------------------------------------------

def select_pfz(
    pfz_candidates: dict[str, Any],
    pfz_id: str
) -> dict[str, Any] | None:
    """
    Select one PFZ from the returned PFZ dictionary.

    Example:
        select_pfz(result["pfz_zones"], "pfz1")
    """

    if not pfz_candidates:
        return None

    pfz_id = pfz_id.lower().strip()

    return pfz_candidates.get(
        pfz_id
    )

