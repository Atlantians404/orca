from ai.agent_state import AgentState
from .main import run_risk_engine

async def risk_engine_node(state: AgentState) -> dict:
    agent_data = state.get("agent_data", {})

    risk_result = run_risk_engine(agent_data)

    return {
        "risk_result": risk_result,
        "workflow_status": "COMPLETED"
    }