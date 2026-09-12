import asyncio

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from ai.agent_state import AgentState

from ai.graph.nodes import (
    location_node,
    time_node,
    pfz_node,
    data_collection_node,
)


def build_test_graph():

    graph = StateGraph(AgentState)

    # Only the nodes we want to test
    graph.add_node("location", location_node)
    graph.add_node("time", time_node)
    graph.add_node("pfz", pfz_node)
    graph.add_node("data_collection", data_collection_node)

    # ---------------------------------------------------------
    # Graph path
    # ---------------------------------------------------------

    graph.add_edge(START, "location")
    graph.add_edge("location", "time")
    graph.add_edge("time", "pfz")
    graph.add_edge("pfz", "data_collection")
    graph.add_edge("data_collection", END)

    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer
    )


app_graph = build_test_graph()


async def run_test(
    test_name,
    location,
    time_response,
):

    print("\n")
    print("=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)

    thread_id = f"test-{test_name}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # ---------------------------------------------------------
    # Initial state
    # ---------------------------------------------------------

    initial_state = {
        "thread_id": thread_id,

        "prompt": "Find marine conditions for fishing.",

        "conversation_summary": None,

        "query_type": "planning",

        "location": None,

        "time_context": None,

        "distance_km": 50.0,

        "pfz_candidates": {},

        "selected_pfz_name": None,

        "selected_pfz": None,

        "agent_data": {},

        "risk_result": None,

        "route_required": False,

        "route_result": None,

        "response": None,

        "pending_action": None,

        "workflow_status": "STARTED",
    }

    # ---------------------------------------------------------
    # Start graph
    # ---------------------------------------------------------

    await app_graph.ainvoke(
        initial_state,
        config=config
    )

    # ---------------------------------------------------------
    # Handle HITL
    # ---------------------------------------------------------

    while True:

        state = await app_graph.aget_state(config)

        if not state.interrupts:
            break

        interrupt_data = state.interrupts[0].value

        action = interrupt_data.get("action")

        print(f"\nHITL: {action}")

        # -----------------------------------------------------
        # Location
        # -----------------------------------------------------

        if action == "GET_LOCATION":

            print(
                "→ Providing test location:"
            )

            print(location)

            user_response = location

        # -----------------------------------------------------
        # Time
        # -----------------------------------------------------

        elif action == "GET_TIME":

            print(
                "→ Providing test time:"
            )

            print(time_response)

            user_response = time_response

        # -----------------------------------------------------
        # Anything after Data Collection is NOT expected
        # -----------------------------------------------------

        else:

            print(
                f"\n❌ Unexpected HITL action: {action}"
            )

            return

        # -----------------------------------------------------
        # Resume
        # -----------------------------------------------------

        await app_graph.ainvoke(
            Command(
                resume=user_response
            ),
            config=config
        )

    # ---------------------------------------------------------
    # Get final state
    # ---------------------------------------------------------

    state = await app_graph.aget_state(config)

    values = state.values

    # ---------------------------------------------------------
    # Print location
    # ---------------------------------------------------------

    print("\n" + "-" * 70)
    print("LOCATION")
    print("-" * 70)

    print(values.get("location"))

    # ---------------------------------------------------------
    # Print time
    # ---------------------------------------------------------

    print("\n" + "-" * 70)
    print("TIME")
    print("-" * 70)

    print(values.get("time_context"))

    # ---------------------------------------------------------
    # Print PFZ candidates
    # ---------------------------------------------------------

    print("\n" + "-" * 70)
    print("PFZ CANDIDATES")
    print("-" * 70)

    pfz_candidates = values.get(
        "pfz_candidates",
        {}
    )

    print(
        f"Total PFZs: {len(pfz_candidates)}"
    )

    for name, pfz in pfz_candidates.items():

        print(f"\n{name}")

        print(
            f"  Latitude: "
            f"{pfz.get('latitude')}"
        )

        print(
            f"  Longitude: "
            f"{pfz.get('longitude')}"
        )

        print(
            f"  Distance: "
            f"{pfz.get('distance_from_source_km')}"
        )

        print(
            f"  Direction: "
            f"{pfz.get('direction')}"
        )

    # ---------------------------------------------------------
    # Print Data Collection
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("DATA COLLECTION AGENT")
    print("=" * 70)

    agent_data = values.get(
        "agent_data",
        {}
    )

    if not agent_data:

        print("\n❌ No agent_data returned.")

        return

    print(
        f"\nPFZs collected: "
        f"{len(agent_data)}"
    )

    for pfz_name, time_data in agent_data.items():

        print("\n" + "-" * 60)

        print(
            f"PFZ: {pfz_name}"
        )

        print("-" * 60)

        for collection_time, data in time_data.items():

            print(
                f"\nTime: {collection_time}"
            )

            print("\nMarine:")

            print(
                data.get("marine")
            )

            print("\nWeather:")

            print(
                data.get("weather")
            )

            print("\nGeo:")

            print(
                data.get("geo")
            )

    # ---------------------------------------------------------
    # Verify Risk Engine did NOT run
    # ---------------------------------------------------------

    print("\n" + "-" * 70)
    print("STOP CHECK")
    print("-" * 70)

    if values.get("risk_result"):

        print(
            "❌ Risk Engine was executed!"
        )

    else:

        print(
            "✅ Risk Engine was NOT executed."
        )

    print("\n" + "=" * 70)

    print(
        f"✅ {test_name} FINISHED"
    )

    print("=" * 70)


async def main():

    # =========================================================
    # CASE 1
    # One location / one time
    # =========================================================

    await run_test(
        test_name="one-pfz-one-time",

        location={
            "latitude": 13.08,
            "longitude": 80.27,
        },

        time_response={
            "date": "2026-08-30",
            "start_time": "08:00",
            "end_time": None,
        },
    )

    # =========================================================
    # CASE 2
    # Different time
    # =========================================================

    await run_test(
        test_name="one-pfz-different-time",

        location={
            "latitude": 13.08,
            "longitude": 80.27,
        },

        time_response={
            "date": "2026-08-30",
            "start_time": "12:00",
            "end_time": None,
        },
    )


if __name__ == "__main__":

    asyncio.run(main())