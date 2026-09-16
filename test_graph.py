import asyncio
from langgraph.types import Command
from ai.graph.graph import app_graph

THREAD_ID = "test-thread-pfz-route-001"

config = {
    "configurable": {
        "thread_id": THREAD_ID,
    }
}


def separator(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_interrupts(result):
    interrupts = result.get("__interrupt__")

    if not interrupts:
        return

    separator("INTERRUPT")

    for interrupt in interrupts:
        value = interrupt.value

        print("Action :", value.get("action"))
        print("Message:", value.get("message"))

        options = value.get("options") or []

        if not options:
            continue

        print("\nOptions:")

        for i, option in enumerate(options, 1):
            if isinstance(option, str):
                print(f"{i}. {option}")
                continue

            if isinstance(option, dict):
                name = option.get("pfz_name", option.get("name", "Unknown PFZ"))
                times = option.get("times") or []

                if times and isinstance(times[0], dict):
                    t = times[0]
                    print(
                        f"{i}. {name} | "
                        f"Risk: {t.get('risk_score')} | "
                        f"Level: {t.get('risk_level')} | "
                        f"Time: {t.get('time')}"
                    )
                else:
                    print(f"{i}. {name}")
                continue

            print(f"{i}. {option}")


def print_state(state):
    separator("CURRENT STATE")

    print("\n--- WORKFLOW ---")
    print("workflow_status :", state.get("workflow_status"))
    print("pending_action  :", state.get("pending_action"))
    print("query_type      :", state.get("query_type"))
    print("route_required  :", state.get("route_required"))

    print("\n--- LOCATION ---")
    print("location        :", state.get("location"))
    print("distance_km     :", state.get("distance_km"))

    print("\n--- TIME ---")
    time_context = state.get("time_context")
    print("time_context    :", time_context)

    if time_context:
        print("timezone        :", getattr(time_context, "timezone", None))
        print("slots           :", getattr(time_context, "slots", None))

    print("\n--- PFZ ---")
    candidates = state.get("pfz_candidates", {})
    print(
        "PFZ count       :",
        len(candidates) if isinstance(candidates, (dict, list)) else 0,
    )
    print("selected_pfz_name:", state.get("selected_pfz_name"))
    print("selected_pfz     :", state.get("selected_pfz"))

    print("\n--- DATA ---")
    agent_data = state.get("agent_data", {})
    print(
        "agent_data count:",
        len(agent_data) if isinstance(agent_data, dict) else 0,
    )
    if isinstance(agent_data, dict):
        print("agent_data keys  :", list(agent_data.keys())[:20])

    print("\n--- RISK ---")
    print(state.get("risk_result"))

    print("\n--- ROUTE ---")
    print(state.get("route_result"))

    print("\n--- RESPONSE ---")
    print(state.get("response"))

    print("\n--- ERROR ---")
    print("error_message   :", state.get("error_message"))
    print("cancellation    :", state.get("cancellation_reason"))


async def main():

    # ========================================================
    # STEP 1 - INITIAL REQUEST
    # ========================================================

    separator("STEP 1 - INITIAL REQUEST")

    prompt = "Plan a fishing trip with route"
    print("User:", prompt)

    result = await app_graph.ainvoke(
        {
            "thread_id": THREAD_ID,
            "prompt": prompt,
            "conversation_summary": "",
        },
        config=config,
    )

    print_interrupts(result)

    # ========================================================
    # STEP 2 - LOCATION
    # ========================================================

    separator("STEP 2 - PROVIDE LOCATION")

    location = {
        "latitude": 13.0827,
        "longitude": 80.2707,
    }

    print("User:", location)

    result = await app_graph.ainvoke(
        Command(resume=location),
        config=config,
    )

    print_interrupts(result)

    # ========================================================
    # STEP 3 - TIME
    # ========================================================

    separator("STEP 3 - PROVIDE TIME")

    user_time = "tomorrow at 6 AM"
    print("User:", user_time)

    result = await app_graph.ainvoke(
        Command(resume=user_time),
        config=config,
    )

    print_interrupts(result)

    # ========================================================
    # STEP 4 - PFZ SELECTION
    # ========================================================

    separator("STEP 4 - SELECT PFZ")

    interrupts = result.get("__interrupt__")

    if not interrupts:
        print("❌ No interrupt returned after time.")
        print_state(result)
        return

    interrupt_value = interrupts[0].value
    action = interrupt_value.get("action")

    print("Pending action:", action)

    if action != "SELECT_PFZ":
        print("❌ Expected SELECT_PFZ.")
        print_state(result)
        return

    options = interrupt_value.get("options") or []

    if not options:
        print("❌ No PFZ options available.")
        print_state(result)
        return

    print("\nAvailable PFZs:")

    for i, option in enumerate(options, 1):
        if isinstance(option, dict):
            name = option.get("pfz_name", option.get("name"))
            print(f"{i}. {name}")
        else:
            print(f"{i}. {option}")

    # Select the FIRST actual PFZ returned by the graph.
    first_option = options[0]

    if isinstance(first_option, dict):
        selected_pfz = first_option.get("pfz_name")
    else:
        selected_pfz = first_option

    if not selected_pfz:
        print("❌ Could not determine PFZ name.")
        print_state(result)
        return

    print("\nUser selected:", selected_pfz)

    # ========================================================
    # RESUME WITH PFZ
    # ========================================================

    result = await app_graph.ainvoke(
        Command(resume=selected_pfz),
        config=config,
    )

    print_interrupts(result)

    # ========================================================
    # STEP 5 - FINAL RESULT
    # ========================================================

    separator("STEP 5 - FINAL RESULT")
    print_state(result)

    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    separator("FINAL VALIDATION")

    selected_name = result.get("selected_pfz_name")
    selected_pfz_object = result.get("selected_pfz")
    route_result = result.get("route_result")
    response = result.get("response")
    workflow_status = result.get("workflow_status")
    interrupts = result.get("__interrupt__")

    print("Workflow status :", workflow_status)
    print("Selected PFZ    :", selected_name)
    print(
        "Selected PFZ obj:",
        "✅ EXISTS" if selected_pfz_object else "❌ MISSING",
    )
    print(
        "Route result    :",
        "✅ EXISTS" if route_result else "❌ MISSING",
    )
    print(
        "Response        :",
        "✅ EXISTS" if response else "❌ MISSING",
    )
    print(
        "Interrupt       :",
        "⏸️ WAITING" if interrupts else "✅ NONE",
    )

    if (
        selected_name
        and selected_pfz_object
        and route_result
        and response
        and not interrupts
    ):
        print("\n🎉 FULL PLANNING FLOW COMPLETED!")

    elif selected_name and selected_pfz_object:
        print("\n⚠️ PFZ SELECTION SUCCEEDED.")
        print("But route generation did not complete.")
        print_state(result)

    else:
        print("\n❌ FULL FLOW DID NOT COMPLETE.")
        print_state(result)


if __name__ == "__main__":
    asyncio.run(main())