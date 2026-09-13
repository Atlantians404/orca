import json

from pathlib import Path

from fastapi import APIRouter


router = APIRouter(
    prefix="/api",
    tags=["Maps"]
)


@router.get("/marine-zones")
async def get_marine_zones():

    file_path = Path("data/restricted_zones/restricted_zones.json")

    with open(file_path, "r") as file:
        data = json.load(file)

    return data