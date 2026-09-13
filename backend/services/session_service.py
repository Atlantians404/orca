from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.sessions import Session
from backend.schemas.session import (
    SessionCreate,
    SessionUpdate,
)

from backend.core.exceptions import not_found


# ==================================================
# CREATE
# ==================================================

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


# ==================================================
# GET ALL - RECENT + PAGINATED
# ==================================================

async def get_user_sessions(
    user_id: int,
    page: int,
    limit: int,
    db: AsyncSession
):
    # Get total number of non-archived sessions
    count_result = await db.execute(
        select(func.count())
        .select_from(Session)
        .where(
            Session.user_id == user_id,
            Session.is_archived.is_(False)
        )
    )

    total = count_result.scalar_one()

    # Calculate offset
    offset = (page - 1) * limit

    # Get recent non-archived sessions
    result = await db.execute(
        select(Session)
        .where(
            Session.user_id == user_id,
            Session.is_archived.is_(False)
        )
        .order_by(
            Session.is_pinned.desc(),
            Session.updated_at.desc()
        )
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


# ==================================================
# GET PINNED - RECENT + PAGINATED
# ==================================================

async def get_pinned_sessions(
    user_id: int,
    page: int,
    limit: int,
    db: AsyncSession
):
    # Get total pinned sessions
    count_result = await db.execute(
        select(func.count())
        .select_from(Session)
        .where(
            Session.user_id == user_id,
            Session.is_pinned.is_(True),
            Session.is_archived.is_(False)
        )
    )

    total = count_result.scalar_one()

    # Calculate offset
    offset = (page - 1) * limit

    # Get recent pinned sessions
    result = await db.execute(
        select(Session)
        .where(
            Session.user_id == user_id,
            Session.is_pinned.is_(True),
            Session.is_archived.is_(False)
        )
        .order_by(Session.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )

    sessions = list(result.scalars().all())

    pages = (total + limit - 1) // limit

    return {
        "items": sessions,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


# ==================================================
# PIN
# ==================================================

async def pin_session(
    session_id: int,
    user_id: int,
    db: AsyncSession
) -> Session:

    session = await get_session(
        session_id,
        user_id,
        db
    )

    session.is_pinned = True

    await db.commit()
    await db.refresh(session)

    return session


# ==================================================
# UNPIN
# ==================================================

async def unpin_session(
    session_id: int,
    user_id: int,
    db: AsyncSession
) -> Session:

    session = await get_session(
        session_id,
        user_id,
        db
    )

    session.is_pinned = False

    await db.commit()
    await db.refresh(session)

    return session


# ==================================================
# GET ARCHIVED - RECENT + PAGINATED
# ==================================================

async def get_archived_sessions(
    user_id: int,
    page: int,
    limit: int,
    db: AsyncSession
):
    # Get total archived sessions
    count_result = await db.execute(
        select(func.count())
        .select_from(Session)
        .where(
            Session.user_id == user_id,
            Session.is_archived.is_(True)
        )
    )

    total = count_result.scalar_one()

    # Calculate offset
    offset = (page - 1) * limit

    # Get recent archived sessions
    result = await db.execute(
        select(Session)
        .where(
            Session.user_id == user_id,
            Session.is_archived.is_(True)
        )
        .order_by(Session.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )

    sessions = list(result.scalars().all())

    pages = (total + limit - 1) // limit

    return {
        "items": sessions,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


# ==================================================
# ARCHIVE
# ==================================================

async def archive_session(
    session_id: int,
    user_id: int,
    db: AsyncSession
) -> Session:

    session = await get_session(
        session_id,
        user_id,
        db
    )

    session.is_archived = True

    await db.commit()
    await db.refresh(session)

    return session


# ==================================================
# UNARCHIVE
# ==================================================

async def unarchive_session(
    session_id: int,
    user_id: int,
    db: AsyncSession
) -> Session:

    session = await get_session(
        session_id,
        user_id,
        db
    )

    session.is_archived = False

    await db.commit()
    await db.refresh(session)

    return session


# ==================================================
# GET ONE
# ==================================================

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


# ==================================================
# UPDATE
# ==================================================

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


# ==================================================
# DELETE
# ==================================================

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