from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from ai.agent_state import AgentState
from ai.orchestrator import orchestrate

from ai.graph.routing import (
    route_query,
    route_after_pfz_selection,
)

from ai.graph.nodes import (
    general_node,
    safety_node,
    planning_node,
    location_node,
    time_node,
    pfz_node,
    data_collection_node,
    risk_node,
    pfz_selection_node,
    route_node,
    final_response_node,
)


def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("orchestrator", orchestrate)
    graph.add_node("general", general_node)
    graph.add_node("safety", safety_node)
    graph.add_node("planning", planning_node)
    graph.add_node("location", location_node)
    graph.add_node("time", time_node)
    graph.add_node("pfz", pfz_node)
    graph.add_node("data_collection", data_collection_node)
    graph.add_node("risk", risk_node)
    graph.add_node("pfz_selection", pfz_selection_node)
    graph.add_node("route", route_node)
    graph.add_node("final_response", final_response_node)

    # Entry
    graph.add_edge(START, "orchestrator")

    # Query routing
    graph.add_conditional_edges(
        "orchestrator",
        route_query,
        {
            "general": "general",
            "safety": "location",
            "planning": "location",
        },
    )

    # General query
    graph.add_edge("general", END)

    # Planning / safety workflow
    graph.add_edge("location", "time")
    graph.add_edge("time", "pfz")
    graph.add_edge("pfz", "data_collection")
    graph.add_edge("data_collection", "risk")
    graph.add_edge("risk", "pfz_selection")

    # PFZ selection
    graph.add_conditional_edges(
        "pfz_selection",
        route_after_pfz_selection,
        {
            "route": "route",
            "final_response": "final_response",
        },
    )

    # Route
    graph.add_edge("route", "final_response")

    # Response
    graph.add_edge("final_response", END)

    # HITL checkpointing
    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)


app_graph = build_graph()