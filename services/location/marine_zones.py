import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env from ORCA root
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

def get_db():
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI not found.")
    client = AsyncIOMotorClient(mongo_uri)
    return client["ORCA"]


async def is_protected(latitude: float, longitude: float) -> bool:

    db = get_db()
    point = {
        "type": "Point",
        "coordinates": [longitude, latitude]
    }

    result = await db["protected_zones"].find_one({
        "geometry": {
            "$geoIntersects": {
                "$geometry": point
            }
        }
    })

    return result is not None


async def is_restricted(latitude: float, longitude: float) -> bool:

    db = get_db()
    point = {
        "type": "Point",
        "coordinates": [longitude, latitude]
    }

    result = await db["restricted_zones"].find_one({
        "geometry": {
            "$geoIntersects": {
                "$geometry": point
            }
        }
    })

    return result is not None