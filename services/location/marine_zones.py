import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env from ORCA root
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client["ORCA"]

protected_collection = db["protected_zones"]
restricted_collection = db["restricted_zones"]


def is_protected(latitude: float, longitude: float) -> bool:

    point = {
        "type": "Point",
        "coordinates": [longitude, latitude]
    }

    result = protected_collection.find_one({
        "geometry": {
            "$geoIntersects": {
                "$geometry": point
            }
        }
    })

    return result is not None


def is_restricted(latitude: float, longitude: float) -> bool:

    point = {
        "type": "Point",
        "coordinates": [longitude, latitude]
    }

    result = restricted_collection.find_one({
        "geometry": {
            "$geoIntersects": {
                "$geometry": point
            }
        }
    })

    return result is not None

