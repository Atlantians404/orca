import asyncio
from pprint import pprint

from langgraph.types import Command

from ai.graph.graph import app_graph


# ============================================================
# CONFIG
# ============================================================

THREAD_ID = "test-thread-time-debug"

config = {
    "configurable": {
        "thread_id": THREAD_ID
    }
}


# ============================================================
# STATE DEBUG
# ============================================================

async def print_state(title: str):
    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)

    state = await app_graph.aget_state(config)

    values = state.values

    print("\n--- WORKFLOW ---")
    print("workflow_status :", values.get("workflow_status"))
    print("pending_action  :", values.get("pending_action"))
    print("query_type      :", values.get("query_type"))
    print("route_required  :", values.get("route_required"))

    print("\n--- LOCATION ---")
    print("location        :", values.get("location"))
    print("distance_km     :", values.get("distance_km"))

    print("\n--- TIME ---")
    print("time_context    :", values.get("time_context"))

    if values.get("time_context"):
        time_context = values["time_context"]

        print("timezone        :", getattr(time_context, "timezone", None))
        print("slots           :", getattr(time_context, "slots", None))

        if getattr(time_context, "slots", None):
            for i, slot in enumerate(time_context.slots, 1):
                print(f"  Slot {i}:")
                print("    date       :", getattr(slot, "date", None))
                print("    start_time :", getattr(slot, "start_time", None))
                print("    end_time   :", getattr(slot, "end_time", None))

    print("\n--- PFZ ---")
    pfz_candidates = values.get("pfz_candidates")

    if isinstance(pfz_candidates, dict):
        print("PFZ count      :", len(pfz_candidates))
    elif isinstance(pfz_candidates, list):
        print("PFZ count      :", len(pfz_candidates))
    else:
        print("PFZ candidates :", pfz_candidates)

    print("selected_pfz_name :", values.get("selected_pfz_name"))
    print("selected_pfz      :", values.get("selected_pfz"))

    print("\n--- DATA ---")
    agent_data = values.get("agent_data")

    if isinstance(agent_data, dict):
        print("agent_data keys :", list(agent_data.keys())[:10])
        print("agent_data count:", len(agent_data))
    else:
        print("agent_data :", agent_data)

    print("\n--- RISK ---")
    pprint(values.get("risk_result"))

    print("\n--- ROUTE ---")
    pprint(values.get("route_result"))

    print("\n--- RESPONSE ---")
    pprint(values.get("response"))

    print("\n--- ERROR ---")
    print("error_message      :", values.get("error_message"))
    print("cancellation_reason:", values.get("cancellation_reason"))

    print("\n--- INTERRUPTS ---")
    print(state.tasks)

    print("=" * 80)


# ============================================================
# GRAPH RESULT DEBUG
# ============================================================

def print_result(title: str, result):
    print("\n")
    print("#" * 80)
    print(title)
    print("#" * 80)

    print("\nResult:")
    pprint(result)

    print("\nInterrupts:")

    if "__interrupt__" in result:
        pprint(result["__interrupt__"])
    else:
        print("No __interrupt__")

    print("\nState returned by invoke:")
    pprint(result)

    print("#" * 80)


# ============================================================
# MAIN TEST
# ============================================================

async def main():

    print("\n")
    print("*" * 80)
    print("ORCA GRAPH FULL HITL TEST")
    print("*" * 80)

    print("\nThread ID:", THREAD_ID)

    # ========================================================
    # STEP 1
    # ========================================================

    print("\n\nSTEP 1")
    print("-" * 80)

    user_message = "Plan a fishing trip with route"

    print("User:", user_message)

    result = await app_graph.ainvoke(
        {
            "thread_id": THREAD_ID,
            "prompt": user_message,
            "conversation_summary": "",
        },
        config=config,
    )

    print_result("STEP 1 RESULT", result)

    await print_state("STATE AFTER STEP 1")

    # ========================================================
    # STEP 2 - LOCATION
    # ========================================================

    print("\n\nSTEP 2")
    print("-" * 80)

    location = {
        "latitude": 13.0827,
        "longitude": 80.2707,
    }

    print("User:", location)

    result = await app_graph.ainvoke(
        Command(resume=location),
        config=config,
    )

    print_result("STEP 2 RESULT", result)

    await print_state("STATE AFTER LOCATION")

    # ========================================================
    # STEP 3 - TIME
    # ========================================================

    print("\n\nSTEP 3")
    print("-" * 80)

    user_time = "tomorrow at 6 AM"

    print("User:", user_time)

    result = await app_graph.ainvoke(
        Command(resume=user_time),
        config=config,
    )

    print_result("STEP 3 RESULT", result)

    # --------------------------------------------------------
    # IMPORTANT:
    # Check state immediately after time processing
    # --------------------------------------------------------

    await print_state("STATE IMMEDIATELY AFTER TIME")

    # ========================================================
    # EXPLICIT TIME CHECK
    # ========================================================

    print("\n\n")
    print("=" * 80)
    print("TIME CONTEXT CHECK")
    print("=" * 80)

    state = await app_graph.aget_state(config)

    time_context = state.values.get("time_context")

    if time_context is None:

        print("\n❌ TIME CONTEXT IS NONE")

        print("\nThis means the time node did NOT successfully store")
        print("the parsed TimeContext in graph state.")

    else:

        print("\n✅ TIME CONTEXT EXISTS")

        print("\nTimeContext:")
        pprint(time_context)

        slots = getattr(time_context, "slots", None)

        if slots:

            print("\n✅ TIME SLOTS EXIST")

            for slot in slots:
                print("\nSlot:")
                print("  date      :", getattr(slot, "date", None))
                print("  start     :", getattr(slot, "start_time", None))
                print("  end       :", getattr(slot, "end_time", None))

        else:

            print("\n❌ TIME SLOTS ARE EMPTY")

    print("=" * 80)

    # ========================================================
    # STEP 4 - PFZ SELECTION
    # ========================================================

    print("\n\nSTEP 4")
    print("-" * 80)

    print("Checking whether PFZ selection is required...")

    state = await app_graph.aget_state(config)

    print("\nCurrent workflow status:")
    print(state.values.get("workflow_status"))

    print("\nPending action:")
    print(state.values.get("pending_action"))

    print("\nSelected PFZ:")
    print(state.values.get("selected_pfz_name"))

    print("\nRisk result:")
    pprint(state.values.get("risk_result"))

    # --------------------------------------------------------
    # Only resume PFZ if the graph actually reached selection
    # --------------------------------------------------------

    pending_action = state.values.get("pending_action")

    if pending_action == "SELECT_PFZ":

        pfz_name = "Kanathur Reddy Kuppam"

        print("\nUser selects PFZ:")
        print(pfz_name)

        result = await app_graph.ainvoke(
            Command(resume=pfz_name),
            config=config,
        )

        print_result("STEP 4 RESULT", result)

        await print_state("STATE AFTER PFZ SELECTION")

    else:

        print("\n⚠️ PFZ selection interrupt was NOT reached.")

        print("pending_action:", pending_action)

    # ========================================================
    # FINAL STATE
    # ========================================================

    await print_state("FINAL GRAPH STATE")

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    state = await app_graph.aget_state(config)
    values = state.values

    print("\n")
    print("*" * 80)
    print("FINAL TEST SUMMARY")
    print("*" * 80)

    print("\nQuery type       :", values.get("query_type"))
    print("Route required   :", values.get("route_required"))
    print("Location         :", values.get("location"))
    print("Time context     :", values.get("time_context"))
    print("Selected PFZ     :", values.get("selected_pfz_name"))
    print("Workflow status  :", values.get("workflow_status"))
    print("Pending action   :", values.get("pending_action"))

    print("\nRisk result:")
    pprint(values.get("risk_result"))

    print("\nRoute result:")
    pprint(values.get("route_result"))

    print("\nResponse:")
    pprint(values.get("response"))

    print("\n")
    print("*" * 80)
    print("TEST FINISHED")
    print("*" * 80)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())