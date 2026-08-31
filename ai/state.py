from typing import TypedDict, Any

from schemas.location import Location
from schemas.time import TimeContext
from schemas.agent_response import AgentResponse


class AgentState(TypedDict, total=False):

    thread_id: str
    prompt: str
    conversation_summary: str | None

    location: Location | None
    time_context: TimeContext | None
    distance_km: float | None

    query_type: str | None

    pfz_candidates: list[dict[str, Any]]
    selected_pfz_id: str | None
    selected_pfz: dict | None

    agent_data: dict[str, Any]

    risk_result: dict[str, Any] | None

    route_required: bool
    route_result: dict[str, Any] | None

    response: AgentResponse | None

    pending_action: str | None
    workflow_status: str