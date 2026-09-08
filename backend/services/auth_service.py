from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.users import User
from backend.schemas.auth import (
    RegisterRequest,
    LoginRequest,
)

from backend.utils.auth_util import (
    hash_password,
    verify_password,
    create_access_token,
)

from backend.core.exceptions import (
    unauthorized,
    conflict,
)


# ==================================================
# REGISTER USER
# ==================================================

async def register_user(
    data: RegisterRequest,
    db: AsyncSession
) -> User:

    result = await db.execute(
        select(User).where(User.email == data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        conflict("Email already registered")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="USER",
        language="en"
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


# ==================================================
# LOGIN USER
# ==================================================

async def login_user(
    data: LoginRequest,
    db: AsyncSession
) -> str:

    result = await db.execute(
        select(User).where(User.email == data.email)
    )

    user = result.scalar_one_or_none()

    if not user:
        unauthorized("Invalid email or password")

    if not verify_password(
        data.password,
        user.hashed_password
    ):
        unauthorized("Invalid email or password")

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )

    return token


# ==================================================
# GET CURRENT USER
# ==================================================

async def get_me(
    current_user: User
) -> User:

    return current_user


# ==================================================
# LOGOUT USER
# ==================================================

async def logout_user(
    current_user: User
) -> None:

    # Currently using stateless JWT.
    # There is no server-side token/session to delete.
    # The frontend removes the access token.

    return None