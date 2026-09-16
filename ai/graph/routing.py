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


def route_after_pfz_selection(state: AgentState) -> str:

    workflow_status = state.get(
        "workflow_status"
    )

    # --------------------------------------------------------
    # Cancelled / failed
    # --------------------------------------------------------

    if workflow_status in {
        "CANCELLED",
        "FAILED",
    }:

        return "final_response"

    # --------------------------------------------------------
    # Route ONLY if a PFZ was actually selected
    # --------------------------------------------------------

    selected_pfz = state.get(
        "selected_pfz"
    )

    if (
        state.get("route_required") is True
        and selected_pfz
    ):

        return "route"

    # --------------------------------------------------------
    # No selected PFZ -> do not enter route
    # --------------------------------------------------------

    return "final_response"