from ai.agent_state import AgentState


async def general_node(state: AgentState) -> dict:
    return {
        "response": {
            "message": "This is a general fishing-related request."
        },
        "workflow_status": "COMPLETED"
    }


async def safety_node(state: AgentState) -> dict:
    return {
        "response": {
            "message": "This is a safety assessment request."
        },
        "workflow_status": "COMPLETED"
    }


async def planning_node(state: AgentState) -> dict:
    return {
        "response": {
            "message": "This is a fishing trip planning request."
        },
        "workflow_status": "COMPLETED"
    }