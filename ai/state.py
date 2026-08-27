from typing import TypedDict, Any

from schemas.location import Location
from schemas.time import TimeContext
from schemas.agent_response import AgentResponse


class AgentState(TypedDict):
    prompt: str
    conversation_summary: str | None

    location: Location | None
    time_context: TimeContext | None

    selected_agents: list[str]
    selected_engines: list[str]

    agent_data: dict[str, Any]

    risk_result: dict[str, Any] | None
    route_result: dict[str, Any] | None

    response: AgentResponse | None