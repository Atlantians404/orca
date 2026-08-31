from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)
from services.auth_service import (
    register_user,
    login_user,
)


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
    user = await register_user(data, db)

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
    token = await login_user(data, db)

    return TokenResponse(
        access_token=token
    )

