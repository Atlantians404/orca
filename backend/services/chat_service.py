from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sessions import Session
from models.messages import Message

from core.exceptions import not_found
from config.logging import logger
from config.llm import llm


async def send_message(
    session_id: int,
    user_id: int,
    message: str,
    db: AsyncSession
) -> str:

    # Check session belongs to user
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == user_id
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        not_found("Session")

    # Save user message
    user_message = Message(
        session_id=session_id,
        role="user",
        content=message
    )

    db.add(user_message)

    # Call LLM
    response = await llm.ainvoke(message)

    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=response.content
    )

    db.add(assistant_message)

    await db.commit()

    logger.info(
        "Chat completed - user=%s session=%s",
        user_id,
        session_id
    )

    return response.content

async def get_chat_history(
    session_id: int,
    user_id: int,
    db: AsyncSession
):
    # Check session belongs to user
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == user_id
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        not_found("Session")

    # Get messages in order
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.id.asc())
    )

    messages = result.scalars().all()

    return messages