from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_db

from backend.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionListResponse,
)

from backend.services.session_service import (
    create_session,
    get_user_sessions,
    get_pinned_sessions,
    pin_session,
    unpin_session,
    get_archived_sessions,
    archive_session,
    unarchive_session,
    get_session,
    update_session,
    delete_session,
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
# GET ALL - RECENT + PAGINATED
# ==================================================

@router.get(
    "",
    response_model=SessionListResponse
)
async def get_all(
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    return await get_user_sessions(
        user_id,
        page,
        limit,
        db
    )


# ==================================================
# GET PINNED - RECENT + PAGINATED
# ==================================================

@router.get(
    "/pinned",
    response_model=SessionListResponse
)
async def get_pinned(
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    return await get_pinned_sessions(
        user_id,
        page,
        limit,
        db
    )


# ==================================================
# PIN
# ==================================================

@router.post(
    "/{session_id}/pin",
    response_model=SessionResponse
)
async def pin(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    session = await pin_session(
        session_id,
        user_id,
        db
    )

    logger.info(
        "Session pinned: %s for user: %s",
        session_id,
        user_id
    )

    return session


# ==================================================
# UNPIN
# ==================================================

@router.delete(
    "/{session_id}/pin",
    response_model=SessionResponse
)
async def unpin(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    session = await unpin_session(
        session_id,
        user_id,
        db
    )

    logger.info(
        "Session unpinned: %s for user: %s",
        session_id,
        user_id
    )

    return session


# ==================================================
# GET ARCHIVED - RECENT + PAGINATED
# ==================================================

@router.get(
    "/archived",
    response_model=SessionListResponse
)
async def get_archived(
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    return await get_archived_sessions(
        user_id,
        page,
        limit,
        db
    )


# ==================================================
# ARCHIVE
# ==================================================

@router.post(
    "/{session_id}/archive",
    response_model=SessionResponse
)
async def archive(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    session = await archive_session(
        session_id,
        user_id,
        db
    )

    logger.info(
        "Session archived: %s for user: %s",
        session_id,
        user_id
    )

    return session


# ==================================================
# UNARCHIVE
# ==================================================

@router.delete(
    "/{session_id}/archive",
    response_model=SessionResponse
)
async def unarchive(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    session = await unarchive_session(
        session_id,
        user_id,
        db
    )

    logger.info(
        "Session unarchived: %s for user: %s",
        session_id,
        user_id
    )

    return session


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