from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.types import Command

from ai.graph.graph import app_graph
from ai.services.conversation_summary import (
    update_conversation_summary,
)

from backend.models.sessions import Session
from backend.models.messages import Message


def _get_interrupt(result: dict) -> Any:
    interrupts = result.get("__interrupt__", [])

    if not interrupts:
        return None

    return interrupts[0].value


def _build_response(result: dict) -> dict:
    """
    Convert LangGraph result into a consistent API response.

    HITL interrupt:
        Returns message + pending action + options.

    Normal/final response:
        Preserves the complete structured AgentResponse.
    """

    interrupt = _get_interrupt(result)

    # ---------------------------------------------------------
    # HITL RESPONSE
    # ---------------------------------------------------------

    if interrupt:
        return {
            "message": interrupt.get(
                "message",
                "Additional information is required."
            ),
            "pending_action": interrupt.get("action"),
            "workflow_status": "WAITING_FOR_USER",
            "options": interrupt.get("options"),
            "response_data": None,
        }

    # ---------------------------------------------------------
    # FINAL AGENT RESPONSE
    # ---------------------------------------------------------

    response = result.get("response")

    response_data = None

    if response is None:
        message = ""

    elif hasattr(response, "model_dump"):
        response_data = response.model_dump()
        message = response.message

    elif isinstance(response, dict):
        response_data = response
        message = response.get("message", "")

    else:
        message = str(response)

    return {
        "message": message,
        "pending_action": result.get("pending_action"),
        "workflow_status": result.get(
            "workflow_status",
            "COMPLETED"
        ),
        "options": None,
        "response_data": response_data,
    }


async def _get_session(
    session_id: int,
    user_id: int,
    db: AsyncSession
) -> Session:

    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == user_id
        )
    )

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session


async def send_message(
    session_id: int,
    user_id: int,
    message: str,
    db: AsyncSession
) -> dict:

    session = await _get_session(
        session_id=session_id,
        user_id=user_id,
        db=db
    )

    config = {
        "configurable": {
            "thread_id": str(session_id)
        }
    }

    initial_state = {
        "thread_id": str(session_id),
        "prompt": message,
        "conversation_summary": session.summary,
        "workflow_status": "IN_PROGRESS",
        "route_required": True,
    }

    result = await app_graph.ainvoke(
        initial_state,
        config=config
    )

    response = _build_response(result)

    # ---------------------------------------------------------
    # SAVE USER MESSAGE
    # ---------------------------------------------------------

    user_message = Message(
        session_id=session_id,
        role="user",
        content=message,
        response_data=None
    )

    db.add(user_message)

    # ---------------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # ---------------------------------------------------------

    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=response["message"],
        response_data=response["response_data"],
    )

    db.add(assistant_message)

    # ---------------------------------------------------------
    # UPDATE CONVERSATION SUMMARY
    # ---------------------------------------------------------

    new_summary = await update_conversation_summary(
        existing_summary=session.summary,
        user_message=message,
        assistant_response=response["message"],
    )

    session.summary = new_summary

    await db.commit()

    return response


async def resume_chat(
    session_id: int,
    user_id: int,
    value: Any,
    db: AsyncSession
) -> dict:

    session = await _get_session(
        session_id=session_id,
        user_id=user_id,
        db=db
    )

    config = {
        "configurable": {
            "thread_id": str(session_id)
        }
    }

    result = await app_graph.ainvoke(
        Command(resume=value),
        config=config
    )

    response = _build_response(result)

    # ---------------------------------------------------------
    # SAVE USER HITL RESPONSE
    # ---------------------------------------------------------

    user_message = Message(
        session_id=session_id,
        role="user",
        content=str(value),
        response_data=None
    )

    db.add(user_message)

    # ---------------------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # ---------------------------------------------------------

    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=response["message"],
        response_data=response["response_data"],
    )

    db.add(assistant_message)

    # ---------------------------------------------------------
    # UPDATE CONVERSATION SUMMARY
    # ---------------------------------------------------------

    new_summary = await update_conversation_summary(
        existing_summary=session.summary,
        user_message=str(value),
        assistant_response=response["message"],
    )

    session.summary = new_summary

    await db.commit()

    return response


async def get_chat_history(
    session_id: int,
    user_id: int,
    db: AsyncSession
) -> list[Message]:

    await _get_session(
        session_id=session_id,
        user_id=user_id,
        db=db
    )

    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.id.asc())
    )

    return list(result.scalars().all())