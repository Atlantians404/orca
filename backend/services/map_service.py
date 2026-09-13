from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.maps import Map
from backend.schemas.maps import MapCreate
from backend.core.exceptions import not_found


async def create_map(
    data: MapCreate,
    user_id: int,
    db: AsyncSession
) -> Map:
    map_data = Map(
        user_id=user_id,
        title=data.title,
        route_data=data.route_data
    )

    db.add(map_data)
    await db.commit()
    await db.refresh(map_data)

    return map_data


async def get_user_maps(
    user_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(Map)
        .where(Map.user_id == user_id)
        .order_by(Map.id.desc())
    )

    return list(result.scalars().all())


async def get_map(
    map_id: int,
    user_id: int,
    db: AsyncSession
) -> Map:
    result = await db.execute(
        select(Map)
        .where(
            Map.id == map_id,
            Map.user_id == user_id
        )
    )

    map_data = result.scalar_one_or_none()

    if not map_data:
        not_found("Map")

    return map_data


async def delete_map(
    map_id: int,
    user_id: int,
    db: AsyncSession
) -> None:
    result = await db.execute(
        select(Map)
        .where(
            Map.id == map_id,
            Map.user_id == user_id
        )
    )

    map_data = result.scalar_one_or_none()

    if not map_data:
        not_found("Map")

    await db.delete(map_data)
    await db.commit()