from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from ai.agent_state import AgentState
from ai.orchestrator import orchestrate
from ai.graph.routing import route_query
from ai.graph.nodes import (
    general_node,
    safety_node,
    planning_node,
    location_node,
    time_node,
    pfz_node,
)


def build_graph():

    graph = StateGraph(AgentState)

    # -------------------------
    # Nodes
    # -------------------------

    graph.add_node("orchestrator", orchestrate)

    graph.add_node("general", general_node)
    graph.add_node("safety", safety_node)
    graph.add_node("planning", planning_node)

    graph.add_node("location", location_node)
    graph.add_node("time", time_node)
    graph.add_node("pfz", pfz_node)

    # -------------------------
    # START → Orchestrator
    # -------------------------

    graph.add_edge(
        START,
        "orchestrator"
    )

    # -------------------------
    # Orchestrator → Router
    # -------------------------

    graph.add_conditional_edges(
        "orchestrator",
        route_query,
        {
            "general": "general",
            "safety": "location",
            "planning": "location",
        },
    )

    # -------------------------
    # General → END
    # -------------------------

    graph.add_edge(
        "general",
        END
    )

    # -------------------------
    # Location → Time
    # -------------------------

    graph.add_edge(
        "location",
        "time"
    )

    # -------------------------
    # Time → PFZ
    # -------------------------

    graph.add_edge(
        "time",
        "pfz"
    )

    # -------------------------
    # PFZ → END
    # -------------------------

    graph.add_edge(
        "pfz",
        END
    )

    # -------------------------
    # Checkpointer
    # Required for interrupt/resume
    # -------------------------

    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer
    )


# -------------------------
# Compiled application graph
# -------------------------

app_graph = build_graph()