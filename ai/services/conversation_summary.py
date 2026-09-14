from ai.configs.config import llm
from ai.prompts.conversation_summary_prompt import (
    CONVERSATION_SUMMARY_PROMPT,
)


async def update_conversation_summary(
    existing_summary: str | None,
    user_message: str,
    assistant_response: str,
) -> str:
    """
    Generate an updated compact conversation summary.

    The summary is used as context for future conversation turns.
    """

    prompt = CONVERSATION_SUMMARY_PROMPT.format(
        existing_summary=existing_summary or "",
        user_message=user_message,
        assistant_response=assistant_response,
    )

    response = await llm.ainvoke(prompt)

    summary = response.content.strip()

    if not summary:
        return existing_summary or ""

    return summary