from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sessions import Session
from schemas.session import SessionCreate
from core.exceptions import not_found


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
    db: AsyncSession
) -> list[Session]:

    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(Session.id.desc())
    )

    return list(result.scalars().all())


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