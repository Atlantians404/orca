from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_db
from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MessageResponse,
    ChatResumeRequest,
)
from backend.services.chat_service import (
    send_message,
    resume_chat,
    get_chat_history,
)
from backend.utils.auth_util import verify_token
from backend.config.logging import logger


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
        session_id=data.session_id,
        message=response["message"],
        pending_action=response.get("pending_action"),
        workflow_status=response.get("workflow_status", "COMPLETED"),
        options=response.get("options"),
    )


@router.post("/{session_id}/resume", response_model=ChatResponse)
async def resume(
    session_id: int,
    data: ChatResumeRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = int(token["sub"])

    logger.info(
        "Resume request from user %s, session %s",
        user_id,
        session_id
    )

    response = await resume_chat(
        session_id=session_id,
        user_id=user_id,
        value=data.value,
        db=db
    )

    return ChatResponse(
        session_id=session_id,
        message=response["message"],
        pending_action=response.get("pending_action"),
        workflow_status=response.get(
            "workflow_status",
            "COMPLETED"
        ),
        options=response.get("options"),
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

    logger.info(
        "Chat history request from user %s, session %s",
        user_id,
        session_id
    )

    return await get_chat_history(
        session_id=session_id,
        user_id=user_id,
        db=db
    )