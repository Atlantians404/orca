import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env")

client = MongoClient(MONGO_URI)

db = client["ORCA"]
collection = db["location_cache"]

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


def coordinate_key(latitude, longitude):
    return f"{latitude:.4f},{longitude:.4f}"


async def get_location_from_nominatim(latitude, longitude):
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

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            NOMINATIM_URL,
            params=params,
            headers=headers
        )

    response.raise_for_status()

    data = response.json()
    address = data.get("address", {})

    district = (
        address.get("city")
        or address.get("municipality")
        or address.get("town")
        or address.get("county")
        or address.get("state_district")
    )

    return {
        "district": district,
        "state": address.get("state")
    }


async def get_locations_batch(nodes):
    keys = [
        coordinate_key(node["latitude"], node["longitude"])
        for node in nodes
    ]

    cached_docs = collection.find({
        "coordinate_key": {"$in": keys}
    })

    cached = {
        doc["coordinate_key"]: doc
        for doc in cached_docs
    }

    result = {}

    for node in nodes:
        node_id = node["node_id"]
        latitude = node["latitude"]
        longitude = node["longitude"]

        key = coordinate_key(latitude, longitude)

        # Use cached location
        if key in cached:
            result[node_id] = {
                "district": cached[key].get("district"),
                "state": cached[key].get("state")
            }
            continue

        # Fetch only if not cached
        location = await get_location_from_nominatim(
            latitude,
            longitude
        )

        result[node_id] = location

        collection.update_one(
            {"coordinate_key": key},
            {
                "$set": {
                    "coordinate_key": key,
                    "latitude": latitude,
                    "longitude": longitude,
                    "district": location.get("district"),
                    "state": location.get("state"),
                    "source": "Nominatim",
                    "cached_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )

    return result