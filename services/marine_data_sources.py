import os
import math
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient


# Load .env from D:\ORCA\.env
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)


def get_mongodb_collection():
    """
    Connect to MongoDB and return the PFZ collection.
    """

    mongo_uri = os.getenv("MONGODB_URI")

    if not mongo_uri:
        raise ValueError(
            "MONGO_URI not found in environment."
        )

    client = MongoClient(mongo_uri)

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
    limit: int = 20
) -> dict[str, Any]:
    """
    Find the nearest PFZ candidates from MongoDB.

    Database:
        ORCA

    Collection:
        pfz
    """

    collection = get_mongodb_collection()

    document = collection.find_one({})

    if not document:
        return {
            "state": "pfz_candidates",
            "pfz_candidates": [],
            "count": 0,
            "message": "No PFZ data found in MongoDB."
        }

    pfz_locations = document.get(
        "pfz_locations",
        []
    )

    candidates = []

    for index, pfz in enumerate(
        pfz_locations,
        start=1
    ):

        pfz_latitude = pfz.get("latitude")
        pfz_longitude = pfz.get("longitude")

        if (
            pfz_latitude is None
            or pfz_longitude is None
        ):
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

    candidates.sort(
        key=lambda item:
        item["distance_from_source_km"]
    )

    candidates = candidates[:limit]

    return {
        "state": "pfz_candidates",
        "pfz_candidates": candidates,
        "count": len(candidates),
        "source": document.get("source")
    }


def select_pfz(
    pfz_candidates: list[dict[str, Any]],
    pfz_id: str
) -> dict[str, Any] | None:
    """
    Select a specific PFZ from PFZ candidates.
    """

    pfz_id = pfz_id.upper().strip()

    for pfz in pfz_candidates:

        if pfz.get("id") == pfz_id:
            return pfz

    return None