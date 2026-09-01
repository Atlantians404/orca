from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas.chat import ChatRequest, ChatResponse, MessageResponse
from services.chat_service import send_message, get_chat_history
from utils.auth_util import verify_token
from config.logging import logger

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "",
    response_model=ChatResponse
)
async def chat(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):

    user_id = int(token["sub"])

    logger.info(
        "Chat request from user %s, session %s",
        user_id,
        data.session_id
    )

    response = await send_message(
        session_id=data.session_id,
        user_id=user_id,
        message=data.message,
        db=db
    )

    return ChatResponse(
        message=response
    )

@router.get(
    "/{session_id}/history",
    response_model=list[MessageResponse]
)
async def get_history(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    return await get_chat_history(
        session_id=session_id,
        user_id=user_id,
        db=db
    )