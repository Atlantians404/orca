from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_db

from backend.models.users import User

from backend.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)

from backend.services.auth_service import (
    register_user,
    login_user,
)

from backend.config.logging import logger

# Change this import path if your get_current_user
# is located somewhere else in your project.
from backend.utils.auth_util import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    logger.info(
        "Registration attempt for email: %s",
        data.email
    )

    user = await register_user(
        data,
        db
    )

    logger.info(
        "User registered successfully: %s",
        user.id
    )

    return {
        "message": "User registered successfully"
    }


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    logger.info(
        "Login attempt for email: %s",
        data.email
    )

    token = await login_user(
        data,
        db
    )

    logger.info(
        "User logged in successfully: %s",
        data.email
    )

    return TokenResponse(
        access_token=token
    )


# --------------------------------------------------
# CURRENT USER
# GET /auth/me
# --------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# --------------------------------------------------
# LOGOUT
# POST /auth/logout
# --------------------------------------------------

@router.post(
    "/logout",
    response_model=MessageResponse
)
async def logout(
    current_user: User = Depends(get_current_user)
):
    logger.info(
        "User logged out successfully: %s",
        current_user.id
    )

    return MessageResponse(
        message="Logged out successfully"
    )