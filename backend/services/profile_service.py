from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.profiles import Profile
from backend.schemas.profile import ProfileUpdate
from backend.core.exceptions import not_found


# ==================================================
# GET PROFILE
# ==================================================

async def get_profile(
    user_id: int,
    db: AsyncSession
) -> Profile:

    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == user_id)
    )

    profile = result.scalar_one_or_none()

    if not profile:
        not_found("Profile")

    return profile


# ==================================================
# UPDATE PROFILE
# ==================================================

async def update_profile(
    data: ProfileUpdate,
    user_id: int,
    db: AsyncSession
) -> Profile:

    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == user_id)
    )

    profile = result.scalar_one_or_none()

    if not profile:
        not_found("Profile")

    if data.display_name is not None:
        profile.display_name = data.display_name

    if data.language is not None:
        profile.language = data.language

    await db.commit()
    await db.refresh(profile)

    return profile