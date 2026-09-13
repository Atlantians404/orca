import json
from pathlib import Path

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from backend.database.database import get_db
from backend.schemas.maps import MapCreate, MapResponse
from backend.services.map_service import (
    create_map,
    get_user_maps,
    get_map,
    delete_map,
)
from backend.utils.auth_util import verify_token
from backend.config.logging import logger

from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import RouteRequest


router = APIRouter(
    prefix="/api",
    tags=["Maps"]
)


@router.post("/routes/generate")
async def generate_route(
    data: RouteRequest,
    token: dict = Depends(verify_token)
):
    try:
        result = RouteEngine().generate_routes(
            request=data,
            time=data.time,
            max_routes=3
        )
        return result
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
        
@router.get("/marine-zones")
async def get_marine_zones():
    file_path = Path(
        "data/restricted_zones/restricted_zones.json"
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    return data


@router.post(
    "/maps",
    response_model=MapResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: MapCreate,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    map_data = await create_map(
        data,
        user_id,
        db
    )

    logger.info(
        "Map created: %s for user: %s",
        map_data.id,
        user_id
    )

    return map_data


@router.get(
    "/maps",
    response_model=list[MapResponse]
)
async def get_all(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    return await get_user_maps(
        user_id,
        db
    )


@router.get(
    "/maps/{map_id}",
    response_model=MapResponse
)
async def get_one(
    map_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    return await get_map(
        map_id,
        user_id,
        db
    )


@router.delete(
    "/maps/{map_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(
    map_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    await delete_map(
        map_id,
        user_id,
        db
    )

    logger.info(
        "Map deleted: %s for user: %s",
        map_id,
        user_id
    )

    return None