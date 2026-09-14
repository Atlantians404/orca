from ai.agent_state import AgentState


def route_query(state: AgentState) -> str:
    """
    Route the initial user request to the appropriate workflow.
    """

    query_type = state.get("query_type")

    if query_type == "general":
        return "general"

    if query_type == "safety":
        return "safety"

    if query_type == "planning":
        return "planning"

    # Safe fallback
    return "general"


def route_after_pfz_selection(state: AgentState) -> str:
    """
    Decide whether to generate a route after PFZ selection.

    A cancelled or failed workflow should never continue to routing.
    """

    workflow_status = state.get("workflow_status")

    # Never continue the workflow after cancellation/failure.
    if workflow_status in {"CANCELLED", "FAILED"}:
        return "final_response"

    # Route only when explicitly required.
    if state.get("route_required") is True:
        return "route"

    return "final_response"