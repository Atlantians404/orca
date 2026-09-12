import asyncio
from ai.schemas.time import TimeContext
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from ai.agent_state import AgentState

from ai.graph.nodes import (
    data_collection_node,
    risk_node,
    pfz_selection_node,
)


# ============================================================
# TEST GRAPH
#
# START
#   ↓
# DATA COLLECTION
#   ↓
# RISK ENGINE
#   ↓
# PFZ SELECTION HITL
#   ↓
# END
# ============================================================

def build_test_graph():

    graph = StateGraph(AgentState)

    graph.add_node(
        "data_collection",
        data_collection_node,
    )

    graph.add_node(
        "risk",
        risk_node,
    )

    graph.add_node(
        "pfz_selection",
        pfz_selection_node,
    )

    graph.add_edge(
        START,
        "data_collection",
    )

    graph.add_edge(
        "data_collection",
        "risk",
    )

    graph.add_edge(
        "risk",
        "pfz_selection",
    )

    graph.add_edge(
        "pfz_selection",
        END,
    )

    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer
    )


test_graph = build_test_graph()


# ============================================================
# INITIAL PFZ DATA
#
# This is what normally comes from pfz_node.
# Data Collection will consume this.
# ============================================================

PFZ_CANDIDATES = {
    "pfz_1": {
        "name": "PFZ Zone 1",
        "latitude": 13.371389,
        "longitude": 80.434167,
    },

    "pfz_2": {
        "name": "PFZ Zone 2",
        "latitude": 13.250000,
        "longitude": 80.500000,
    },

    "pfz_3": {
        "name": "PFZ Zone 3",
        "latitude": 13.100000,
        "longitude": 80.600000,
    },
}


# ============================================================
# TIME CONTEXT
#
# We bypass the Time HITL here.
# We already tested Time separately.
# ============================================================

def make_time_context():

    return TimeContext(
        slots=[
            {
                "date": "2026-09-13",
                "start_time": "08:00",
                "end_time": None,
            },
            {
                "date": "2026-09-13",
                "start_time": "12:00",
                "end_time": None,
            },
            {
                "date": "2026-09-13",
                "start_time": "16:00",
                "end_time": None,
            },
        ]
    )


# ============================================================
# PRINT AGENT DATA
# ============================================================

def print_agent_data(agent_data):

    print("\n")
    print("=" * 70)
    print("DATA COLLECTION OUTPUT")
    print("=" * 70)

    for pfz_name, time_data in agent_data.items():

        print(f"\n📍 PFZ: {pfz_name}")

        for timestamp, data in time_data.items():

            print(f"\n🕐 {timestamp}")

            print("\nMarine:")
            print(data.get("marine"))

            print("\nWeather:")
            print(data.get("weather"))

            print("\nGeo:")
            print(data.get("geo"))


# ============================================================
# PRINT RISK RESULT
# ============================================================

def print_risk_result(risk_result):

    print("\n")
    print("=" * 70)
    print("RISK ENGINE OUTPUT")
    print("=" * 70)

    print(risk_result)

    ranked_results = risk_result.get(
        "ranked_results",
        [],
    )

    print("\nRanked PFZ results:")

    for result in ranked_results:

        # Handle both possible formats:
        #
        # Case:
        # PFZ + one time
        #
        # {
        #     pfz_name,
        #     time,
        #     risk_score,
        #     risk_level
        # }
        #
        # Case:
        # PFZ + multiple times
        #
        # {
        #     pfz_name,
        #     times: [...]
        # }

        if "times" in result:

            print(
                f"\nPFZ: {result.get('pfz_name')}"
            )

            for time_result in result["times"]:

                print(
                    f"  {time_result.get('time')}"
                    f" → "
                    f"{time_result.get('risk_score')}"
                    f" "
                    f"{time_result.get('risk_level')}"
                )

        else:

            print(
                f"\nPFZ: {result.get('pfz_name')}"
                f"\nTime: {result.get('time')}"
                f"\nRisk Score: {result.get('risk_score')}"
                f"\nRisk Level: {result.get('risk_level')}"
            )


# ============================================================
# MAIN TEST
# ============================================================

async def test_data_collection_to_risk_to_selection():

    print("\n")
    print("#" * 70)
    print("# DATA COLLECTION → RISK → PFZ SELECTION")
    print("#" * 70)

    thread_id = "integration-data-risk-selection"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # ========================================================
    # INITIAL STATE
    # ========================================================

    initial_state: AgentState = {

        "thread_id": thread_id,

        "pfz_candidates": PFZ_CANDIDATES,

        "time_context": make_time_context(),

        "workflow_status": "IN_PROGRESS",

        "pending_action": None,

    }

    # ========================================================
    # STEP 1
    # DATA COLLECTION → RISK → PFZ SELECTION
    # ========================================================

    print("\n")
    print("=" * 70)
    print("STARTING INTEGRATED GRAPH")
    print("=" * 70)

    result = await test_graph.ainvoke(
        initial_state,
        config=config,
    )

    # ========================================================
    # CHECK INTERRUPT
    # ========================================================

    assert "__interrupt__" in result, (
        "Expected PFZ Selection HITL interrupt, "
        "but graph did not interrupt."
    )

    interrupts = result["__interrupt__"]

    assert interrupts, (
        "Interrupt list is empty."
    )

    interrupt_data = interrupts[0].value

    print("\n")
    print("=" * 70)
    print("PFZ SELECTION HITL INTERRUPT")
    print("=" * 70)

    print(interrupt_data)

    # ========================================================
    # GET CHECKPOINT STATE
    # ========================================================

    current_state = test_graph.get_state(
        config
    ).values

    # ========================================================
    # VERIFY DATA COLLECTION
    # ========================================================

    print_agent_data(
        current_state.get(
            "agent_data",
            {},
        )
    )

    agent_data = current_state.get(
        "agent_data",
        {},
    )

    assert agent_data, (
        "❌ Data Collection produced empty agent_data."
    )

    print("\n✅ Data Collection produced agent_data")

    # ========================================================
    # VERIFY RISK ENGINE
    # ========================================================

    risk_result = current_state.get(
        "risk_result"
    )

    assert risk_result is not None, (
        "❌ Risk Engine did not produce risk_result."
    )

    assert isinstance(
        risk_result,
        dict,
    )

    assert "ranked_results" in risk_result, (
        "❌ ranked_results missing from risk_result."
    )

    ranked_results = risk_result[
        "ranked_results"
    ]

    assert ranked_results, (
        "❌ Risk Engine returned empty ranked_results."
    )

    print_risk_result(
        risk_result
    )

    print("\n✅ Risk Engine produced risk_result")
    print("✅ ranked_results exists")
    print(
        f"✅ Ranked PFZ result count: "
        f"{len(ranked_results)}"
    )

    # ========================================================
    # VERIFY PFZ SELECTION INTERRUPT
    # ========================================================

    assert (
        interrupt_data.get("action")
        == "SELECT_PFZ"
    ), (
        "❌ Expected SELECT_PFZ interrupt."
    )

    options = interrupt_data.get(
        "options",
        [],
    )

    assert options, (
        "❌ PFZ selection options are empty."
    )

    print("\nAvailable selection options:")

    for option in options:

        print(
            f"  {option.get('pfz_name')}"
            f" | "
            f"{option.get('risk_score')}"
            f" | "
            f"{option.get('risk_level')}"
        )

    # ========================================================
    # VERIFY OPTIONS MATCH RISK RESULTS
    # ========================================================

    risk_names = {
        result.get("pfz_name")
        for result in ranked_results
        if result.get("pfz_name")
    }

    option_names = {
        option.get("pfz_name")
        for option in options
        if option.get("pfz_name")
    }

    assert option_names == risk_names, (
        "\n❌ PFZ selection options do not "
        "match Risk Engine results.\n"
        f"Risk: {risk_names}\n"
        f"Options: {option_names}"
    )

    print(
        "\n✅ PFZ selection options "
        "match Risk Engine results"
    )

    # ========================================================
    # SELECT FIRST PFZ
    # ========================================================

    selected_name = options[0].get(
        "pfz_name"
    )

    assert selected_name, (
        "❌ Selected PFZ name is empty."
    )

    print("\n")
    print("=" * 70)
    print("USER SELECTING PFZ")
    print("=" * 70)

    print(
        f"Selected PFZ: {selected_name}"
    )

    # ========================================================
    # RESUME GRAPH
    # ========================================================

    result = await test_graph.ainvoke(
        Command(
            resume=selected_name
        ),
        config=config,
    )

    # ========================================================
    # FINAL STATE
    # ========================================================

    final_state = test_graph.get_state(
        config
    ).values

    print("\n")
    print("=" * 70)
    print("FINAL STATE")
    print("=" * 70)

    print(
        "\nselected_pfz_name:"
    )

    print(
        final_state.get(
            "selected_pfz_name"
        )
    )

    print(
        "\nselected_pfz:"
    )

    print(
        final_state.get(
            "selected_pfz"
        )
    )

    print(
        "\nrisk_result:"
    )

    print(
        final_state.get(
            "risk_result"
        )
    )

    # ========================================================
    # FINAL ASSERTIONS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("RUNNING FINAL ASSERTIONS")
    print("=" * 70)

    # --------------------------------------------------------
    # Data Collection
    # --------------------------------------------------------

    assert final_state.get(
        "agent_data"
    ), (
        "❌ agent_data missing."
    )

    print(
        "✅ Data Collection completed"
    )

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    assert final_state.get(
        "risk_result"
    ), (
        "❌ risk_result missing."
    )

    print(
        "✅ Risk Engine completed"
    )

    # --------------------------------------------------------
    # Selection
    # --------------------------------------------------------

    assert final_state.get(
        "selected_pfz_name"
    ) == selected_name, (
        "❌ selected_pfz_name does not "
        "match user selection."
    )

    print(
        "✅ selected_pfz_name is correct"
    )

    assert final_state.get(
        "selected_pfz"
    ) is not None, (
        "❌ selected_pfz is missing."
    )

    print(
        "✅ selected_pfz is populated"
    )

    # --------------------------------------------------------
    # Risk result must survive selection
    # --------------------------------------------------------

    assert final_state.get(
        "risk_result"
    ) is not None

    print(
        "✅ risk_result preserved after HITL"
    )

    # --------------------------------------------------------
    # No PFZ ID
    # --------------------------------------------------------

    assert "selected_pfz_id" not in final_state, (
        "❌ selected_pfz_id should not exist."
    )

    print(
        "✅ No selected_pfz_id used"
    )

    # --------------------------------------------------------
    # Pending action
    # --------------------------------------------------------

    assert final_state.get(
        "pending_action"
    ) is None

    print(
        "✅ pending_action cleared"
    )

    print("\n")
    print("#" * 70)
    print("# ✅ INTEGRATION TEST PASSED")
    print("#" * 70)

    print(
        "\nData Collection → Risk Engine "
        "→ PFZ Selection HITL works correctly."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        test_data_collection_to_risk_to_selection()
    )