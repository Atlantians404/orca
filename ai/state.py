from typing import TypedDict
from backend.schemas.location import Location
from backend.schemas.time_context import TimeContext
from backend.schemas.response import AgentResponse
class AgentState(TypedDict):
    prompt: str
    conversation_summary: str | None

    location: Location | None
    time_context: TimeContext | None

    selected_agents: list[str]
    selected_engines: list[str]

    agent_data: dict

    risk_result: dict | None
    route_result: dict | None

    response: AgentResponse | None