import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env from ORCA root
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    raise ValueError("MONGO_URI not found.")

client = AsyncIOMotorClient(mongo_uri)
db = client["ORCA"]

protected_collection = db["protected_zones"]
restricted_collection = db["restricted_zones"]


async def is_protected(latitude: float, longitude: float) -> bool:

    point = {
        "type": "Point",
        "coordinates": [longitude, latitude]
    }

    result = await protected_collection.find_one({
        "geometry": {
            "$geoIntersects": {
                "$geometry": point
            }
        }
    })

    return result is not None


async def is_restricted(latitude: float, longitude: float) -> bool:

    point = {
        "type": "Point",
        "coordinates": [longitude, latitude]
    }

    result = await restricted_collection.find_one({
        "geometry": {
            "$geoIntersects": {
                "$geometry": point
            }
        }
    })

    return result is not None