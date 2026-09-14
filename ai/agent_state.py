from typing import TypedDict, Any

from ai.schemas.location import Location
from ai.schemas.time import TimeContext
from ai.schemas.agent_response import AgentResponse


class AgentState(TypedDict, total=False):

    # Conversation / execution
    thread_id: str
    prompt: str
    conversation_summary: str | None

    # User-provided planning information
    location: Location | None
    time_context: TimeContext | None
    distance_km: float | None

    # Query classification
    query_type: str | None

    # PFZ
    pfz_candidates: dict[str, Any]
    selected_pfz_name: str | None
    selected_pfz: dict | None

    # Data collected from external/internal agents
    agent_data: dict[str, Any]

    # Risk
    risk_result: dict[str, Any] | None

    # Route
    route_required: bool
    route_result: dict[str, Any] | None

    # Final response
    response: AgentResponse | None

    # HITL
    pending_action: str | None

    # Workflow lifecycle
    workflow_status: str

    # Error / cancellation
    error_message: str | None
    cancellation_reason: str | None