from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_db

from backend.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse
)

from backend.services.session_service import (
    create_session,
    get_user_sessions,
    get_session,
    update_session,
    delete_session
)

from backend.utils.auth_util import verify_token
from backend.config.logging import logger


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


# ==================================================
# CREATE
# ==================================================

@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    session = await create_session(
        data,
        user_id,
        db
    )

    logger.info(
        "Session created: %s for user: %s",
        session.id,
        user_id
    )

    return session


# ==================================================
# GET ALL
# ==================================================

@router.get(
    "",
    response_model=list[SessionResponse]
)
async def get_all(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    return await get_user_sessions(
        user_id,
        db
    )


# ==================================================
# GET ONE
# ==================================================

@router.get(
    "/{session_id}",
    response_model=SessionResponse
)
async def get_one(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    return await get_session(
        session_id,
        user_id,
        db
    )


# ==================================================
# UPDATE
# ==================================================

@router.patch(
    "/{session_id}",
    response_model=SessionResponse
)
async def update(
    session_id: int,
    data: SessionUpdate,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    session = await update_session(
        session_id,
        data,
        user_id,
        db
    )

    logger.info(
        "Session updated: %s for user: %s",
        session.id,
        user_id
    )

    return session


# ==================================================
# DELETE
# ==================================================

@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    await delete_session(
        session_id,
        user_id,
        db
    )

    logger.info(
        "Session deleted: %s for user: %s",
        session_id,
        user_id
    )

    return None