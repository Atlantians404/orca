from ai.configs.config import llm
from ai.agent_state import AgentState
from ai.prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT

async def orchestrate(state: AgentState) -> dict:
    prompt = state["prompt"]

    message = ORCHESTRATOR_PROMPT.format(prompt=prompt)

    response = await llm.ainvoke(message)

    query_type = response.content.strip().lower()

    if query_type not in {"general", "safety", "planning"}:
        query_type = "general"

    return {
        "query_type": query_type
    }

