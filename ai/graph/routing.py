from ai.agent_state import AgentState


def route_query(state: AgentState) -> str:
    query_type = state.get("query_type")

    if query_type == "general":
        return "general"

    if query_type == "safety":
        return "safety"

    if query_type == "planning":
        return "planning"

    return "general"