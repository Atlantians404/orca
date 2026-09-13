import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


ROOT_DIR = Path(__file__).resolve().parents[3]

load_dotenv(
    ROOT_DIR / ".env"
)

def get_db():
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI not found.")
    client = AsyncIOMotorClient(mongo_uri)
    return client["ORCA"]


def _clean_document(
    document: dict,
) -> dict:

    if not document:
        return document

    document = dict(document)

    if "_id" in document:
        document["_id"] = str(
            document["_id"]
        )

    return document


async def get_restricted_zones() -> list[dict]:

    db = get_db()
    cursor = db["restricted_zones"].find({})

    documents = await cursor.to_list(
        length=None
    )

    return [
        _clean_document(document)
        for document in documents
    ]


async def get_protected_zones() -> list[dict]:

    db = get_db()
    cursor = db["protected_zones"].find({})

    documents = await cursor.to_list(
        length=None
    )

    return [
        _clean_document(document)
        for document in documents
    ]


async def get_route_zones() -> dict:

    restricted, protected = await __import__(
        "asyncio"
    ).gather(
        get_restricted_zones(),
        get_protected_zones(),
    )

    return {
        "restricted": restricted,
        "protected": protected,
    }