import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


async def get_pfz_coordinates(pfz_name: str) -> dict:

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("MONGO_URI not found.")

    client = AsyncIOMotorClient(mongo_uri)

    db = client["ORCA"]
    collection = db["pfz"]

    document = await collection.find_one(
        {
            "pfz_locations.coastal_reference": {
                "$regex": f"^{pfz_name.strip()}$",
                "$options": "i"
            }
        },
        {
            "pfz_locations.$": 1
        }
    )

    if not document:
        raise ValueError(f"PFZ not found: {pfz_name}")

    pfz = document["pfz_locations"][0]

    return {
        "pfz_name": pfz["coastal_reference"],
        "latitude": pfz["latitude"],
        "longitude": pfz["longitude"]
    }