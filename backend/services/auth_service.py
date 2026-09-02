from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.users import User
from backend.schemas.auth import RegisterRequest, LoginRequest

from backend.utils.auth_util import (
    hash_password,
    verify_password,
    create_access_token,
)

from backend.core.exceptions import (
    unauthorized,
    conflict,
)


async def register_user(
    data: RegisterRequest,
    db: AsyncSession
) -> User:

    # Check whether email already exists
    result = await db.execute(
        select(User).where(User.email == data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        conflict("Email already registered")

    # Create user
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="USER"
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


async def login_user(
    data: LoginRequest,
    db: AsyncSession
) -> str:

    # Find user
    result = await db.execute(
        select(User).where(User.email == data.email)
    )

    user = result.scalar_one_or_none()

    if not user:
        unauthorized("Invalid email or password")

    # Verify password
    if not verify_password(
        data.password,
        user.hashed_password
    ):
        unauthorized("Invalid email or password")

    # Create JWT
    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )

    return token