from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_db
from backend.schemas.session import (
    SessionCreate,
    SessionResponse
)
from backend.services.session_service import (
    create_session,
    get_user_sessions,
    get_session
)
from backend.utils.auth_util import verify_token
from backend.config.logging import logger


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


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