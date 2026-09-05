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
    pfz_selection_node,
)


def build_graph():

    graph = StateGraph(AgentState)

    # =====================================================
    # NODES
    # =====================================================

    graph.add_node(
        "orchestrator",
        orchestrate
    )

    graph.add_node(
        "general",
        general_node
    )

    graph.add_node(
        "safety",
        safety_node
    )

    graph.add_node(
        "planning",
        planning_node
    )

    graph.add_node(
        "location",
        location_node
    )

    graph.add_node(
        "time",
        time_node
    )

    graph.add_node(
        "pfz",
        pfz_node
    )

    graph.add_node(
        "pfz_selection",
        pfz_selection_node
    )

    # =====================================================
    # START → ORCHESTRATOR
    # =====================================================

    graph.add_edge(
        START,
        "orchestrator"
    )

    # =====================================================
    # ORCHESTRATOR → ROUTER
    # =====================================================

    graph.add_conditional_edges(
        "orchestrator",
        route_query,
        {
            "general": "general",
            "safety": "location",
            "planning": "location",
        },
    )

    # =====================================================
    # GENERAL → END
    # =====================================================

    graph.add_edge(
        "general",
        END
    )

    # =====================================================
    # LOCATION → TIME
    # =====================================================

    graph.add_edge(
        "location",
        "time"
    )

    # =====================================================
    # TIME → PFZ
    # =====================================================

    graph.add_edge(
        "time",
        "pfz"
    )

    # =====================================================
    # PFZ → PFZ SELECTION
    # =====================================================

    graph.add_edge(
        "pfz",
        "pfz_selection"
    )

    # =====================================================
    # PFZ SELECTION → END
    # =====================================================

    graph.add_edge(
        "pfz_selection",
        END
    )

    # =====================================================
    # CHECKPOINTER
    # Required for interrupt / resume
    # =====================================================

    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer
    )


# =========================================================
# COMPILED APPLICATION GRAPH
# =========================================================

app_graph = build_graph()