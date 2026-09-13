from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.sessions import Session
from backend.schemas.session import (
    SessionCreate,
    SessionUpdate,
)

from backend.core.exceptions import not_found


async def create_session(
    data: SessionCreate,
    user_id: int,
    db: AsyncSession
) -> Session:

    session = Session(
        user_id=user_id,
        title=data.title
    )

    db.add(session)

    await db.commit()
    await db.refresh(session)

    return session


async def get_user_sessions(
    user_id: int,
    page: int,
    limit: int,
    db: AsyncSession
):
    # Get total number of sessions
    count_result = await db.execute(
        select(func.count())
        .select_from(Session)
        .where(Session.user_id == user_id)
    )

    total = count_result.scalar_one()

    # Calculate offset
    offset = (page - 1) * limit

    # Get paginated sessions
    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(Session.id.desc())
        .offset(offset)
        .limit(limit)
    )

    sessions = list(result.scalars().all())

    # Calculate total pages
    pages = (total + limit - 1) // limit

    return {
        "items": sessions,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


async def get_session(
    session_id: int,
    user_id: int,
    db: AsyncSession
) -> Session:

    result = await db.execute(
        select(Session)
        .where(
            Session.id == session_id,
            Session.user_id == user_id
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        not_found("Session")

    return session


async def update_session(
    session_id: int,
    data: SessionUpdate,
    user_id: int,
    db: AsyncSession
) -> Session:

    result = await db.execute(
        select(Session)
        .where(
            Session.id == session_id,
            Session.user_id == user_id
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        not_found("Session")

    if data.title is not None:
        session.title = data.title

    await db.commit()
    await db.refresh(session)

    return session


async def delete_session(
    session_id: int,
    user_id: int,
    db: AsyncSession
) -> None:

    result = await db.execute(
        select(Session)
        .where(
            Session.id == session_id,
            Session.user_id == user_id
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        not_found("Session")

    await db.delete(session)

    await db.commit()