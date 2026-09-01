from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_db
from backend.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)
from backend.services.auth_service import (
    register_user,
    login_user,
)
from backend.config.logging import logger


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    logger.info("Registration attempt for email: %s", data.email)

    user = await register_user(data, db)

    logger.info("User registered successfully: %s", user.id)

    return {
        "message": "User registered successfully",
        "user_id": user.id
    }


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    logger.info("Login attempt for email: %s", data.email)

    token = await login_user(data, db)

    logger.info("User logged in successfully: %s", data.email)

    return TokenResponse(
        access_token=token
    )