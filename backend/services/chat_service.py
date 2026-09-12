from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.types import Command

from ai.graph.graph import app_graph

from backend.models.sessions import Session
from backend.models.messages import Message


def _get_interrupt(result: dict) -> Any:
    interrupts = result.get("__interrupt__", [])

    if not interrupts:
        return None

    return interrupts[0].value


def _build_response(result: dict) -> dict:
    interrupt = _get_interrupt(result)

    if interrupt:
        return {
            "message": interrupt.get(
                "message",
                "Additional information is required."
            ),
            "pending_action": interrupt.get("action"),
            "workflow_status": "WAITING_FOR_USER",
            "options": interrupt.get("options"),
        }

    response = result.get("response")

    if isinstance(response, dict):
        message = response.get("message", "")
    else:
        message = str(response or "")

    return {
        "message": message,
        "pending_action": result.get("pending_action"),
        "workflow_status": result.get(
            "workflow_status",
            "COMPLETED"
        ),
        "options": None,
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

    user_message = Message(
        session_id=session_id,
        role="user",
        content=message,
        response_data=None
    )

    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=response["message"],
        response_data={
            "pending_action": response["pending_action"],
            "workflow_status": response["workflow_status"],
        }
    )

    db.add(user_message)
    db.add(assistant_message)

    await db.commit()

    return response


async def resume_chat(
    session_id: int,
    user_id: int,
    value: Any,
    db: AsyncSession
) -> dict:

    await _get_session(
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

    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=response["message"],
        response_data={
            "pending_action": response["pending_action"],
            "workflow_status": response["workflow_status"],
        }
    )

    db.add(assistant_message)

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