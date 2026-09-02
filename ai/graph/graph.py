from langgraph.graph import StateGraph, START, END

from ai.agent_state import AgentState
from ai.orchestrator import orchestrate
from ai.graph.routing import route_query
from ai.graph.nodes import (
    general_node,
    safety_node,
    planning_node,
)


def build_graph():

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("orchestrator", orchestrate)
    graph.add_node("general", general_node)
    graph.add_node("safety", safety_node)
    graph.add_node("planning", planning_node)

    # START → Orchestrator
    graph.add_edge(START, "orchestrator")

    # Orchestrator → Router
    graph.add_conditional_edges(
        "orchestrator",
        route_query,
        {
            "general": "general",
            "safety": "safety",
            "planning": "planning",
        },
    )

    # End of each flow
    graph.add_edge("general", END)
    graph.add_edge("safety", END)
    graph.add_edge("planning", END)

    return graph.compile()


app_graph = build_graph()