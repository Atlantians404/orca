import os
from pymongo import MongoClient


def get_pfz_coordinates(pfz_name: str) -> dict:

    mongo_uri = "mongodb+srv://jananivenkatesh81_db_user:d8UsyP5KAR8pWJFb@orca-cluster.tznvnez.mongodb.net/?appName=ORCA-Cluster"

    if not mongo_uri:
        raise ValueError("MONGO_URI not found.")

    client = MongoClient(mongo_uri)
    db = client["ORCA"]
    collection = db["pfz"]

    document = collection.find_one(
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
        raise ValueError(
            f"PFZ not found: {pfz_name}"
        )

    pfz = document["pfz_locations"][0]

    return {
        "pfz_name": pfz["coastal_reference"],
        "latitude": pfz["latitude"],
        "longitude": pfz["longitude"]
    }