import json

from ai.configs.config import llm
from ai.agent_state import AgentState
from ai.prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT


async def orchestrate(state: AgentState) -> dict:
    prompt = state["prompt"]

    message = ORCHESTRATOR_PROMPT.format(prompt=prompt)

    response = await llm.ainvoke(message)

    result = json.loads(response.content)

    query_type = result.get("query_type", "general")

    if query_type not in {"general", "safety", "planning"}:
        query_type = "general"

    return {
        "query_type": query_type,
        "distance_km": result.get("distance_km"),
        "selected_pfz_id": result.get("selected_pfz_id"),
        "route_required": result.get("route_required", False),
    }