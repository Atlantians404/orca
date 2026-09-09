from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_db

from backend.schemas.profile import (
    ProfileUpdate,
    ProfileResponse
)

from backend.services.profile_service import (
    get_profile,
    update_profile
)

from backend.utils.auth_util import verify_token
from backend.config.logging import logger


router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


# ==================================================
# GET PROFILE
# ==================================================

@router.get(
    "",
    response_model=ProfileResponse
)
async def get(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    profile = await get_profile(
        user_id,
        db
    )

    return profile


# ==================================================
# UPDATE PROFILE
# ==================================================

@router.patch(
    "",
    response_model=ProfileResponse
)
async def update(
    data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    profile = await update_profile(
        data,
        user_id,
        db
    )

    logger.info(
        "Profile updated for user: %s",
        user_id
    )

    return profile