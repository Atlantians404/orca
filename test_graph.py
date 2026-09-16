import asyncio

from langgraph.types import Command

from ai.graph.graph import app_graph


# ============================================================
# CONFIG
# ============================================================

THREAD_ID = "test-thread-pfz-route-001"

config = {
    "configurable": {
        "thread_id": THREAD_ID,
    }
}


# ============================================================
# HELPERS
# ============================================================

def print_separator(title: str):
    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_interrupts(result):
    """
    Safely print LangGraph interrupt information.

    Options may be:
        - strings
        - dictionaries
    """

    interrupts = result.get("__interrupt__")

    if not interrupts:
        return

    print_separator("INTERRUPT")

    for interrupt in interrupts:

        value = interrupt.value

        print("Action :", value.get("action"))
        print("Message:", value.get("message"))

        options = value.get("options")

        if not options:
            continue

        print("\nOptions:")

        for index, option in enumerate(options, start=1):

            # ------------------------------------------------
            # Option is a string
            # ------------------------------------------------

            if isinstance(option, str):

                print(f"{index}. {option}")

                continue

            # ------------------------------------------------
            # Option is a dictionary
            # ------------------------------------------------

            if isinstance(option, dict):

                pfz_name = option.get("pfz_name")

                times = option.get("times", [])

                if times and isinstance(times, list):

                    time_info = times[0]

                    if isinstance(time_info, dict):

                        print(
                            f"{index}. {pfz_name} | "
                            f"Risk: {time_info.get('risk_score')} | "
                            f"Level: {time_info.get('risk_level')} | "
                            f"Time: {time_info.get('time')}"
                        )

                    else:

                        print(
                            f"{index}. {pfz_name} | "
                            f"Time: {time_info}"
                        )

                else:

                    print(f"{index}. {pfz_name}")

                continue

            # ------------------------------------------------
            # Unknown option type
            # ------------------------------------------------

            print(f"{index}. {option}")


def print_state(state):
    """
    Print important AgentState fields.
    """

    print_separator("CURRENT STATE")

    # ========================================================
    # WORKFLOW
    # ========================================================

    print("\n--- WORKFLOW ---")

    print(
        "workflow_status :",
        state.get("workflow_status"),
    )

    print(
        "pending_action  :",
        state.get("pending_action"),
    )

    print(
        "query_type      :",
        state.get("query_type"),
    )

    print(
        "route_required  :",
        state.get("route_required"),
    )

    # ========================================================
    # LOCATION
    # ========================================================

    print("\n--- LOCATION ---")

    print(
        "location   :",
        state.get("location"),
    )

    print(
        "distance_km:",
        state.get("distance_km"),
    )

    # ========================================================
    # TIME
    # ========================================================

    print("\n--- TIME ---")

    time_context = state.get("time_context")

    print(
        "time_context:",
        time_context,
    )

    if time_context:

        print(
            "timezone:",
            getattr(
                time_context,
                "timezone",
                None,
            ),
        )

        print(
            "slots:",
            getattr(
                time_context,
                "slots",
                None,
            ),
        )

    # ========================================================
    # PFZ
    # ========================================================

    print("\n--- PFZ ---")

    pfz_candidates = state.get(
        "pfz_candidates",
        {},
    )

    print(
        "PFZ count:",
        len(pfz_candidates)
        if isinstance(pfz_candidates, dict)
        else 0,
    )

    print(
        "selected_pfz_name:",
        state.get("selected_pfz_name"),
    )

    print(
        "selected_pfz:",
        state.get("selected_pfz"),
    )

    # ========================================================
    # DATA
    # ========================================================

    print("\n--- DATA ---")

    agent_data = state.get(
        "agent_data",
        {},
    )

    print(
        "agent_data count:",
        len(agent_data)
        if isinstance(agent_data, dict)
        else 0,
    )

    if isinstance(agent_data, dict):

        print(
            "agent_data keys:",
            list(agent_data.keys())[:20],
        )

    # ========================================================
    # RISK
    # ========================================================

    print("\n--- RISK ---")

    risk_result = state.get(
        "risk_result"
    )

    print(risk_result)

    # ========================================================
    # ROUTE
    # ========================================================

    print("\n--- ROUTE ---")

    route_result = state.get(
        "route_result"
    )

    print(route_result)

    # ========================================================
    # RESPONSE
    # ========================================================

    print("\n--- RESPONSE ---")

    response = state.get(
        "response"
    )

    print(response)

    # ========================================================
    # ERROR
    # ========================================================

    print("\n--- ERROR ---")

    print(
        "error_message:",
        state.get("error_message"),
    )

    print(
        "cancellation_reason:",
        state.get("cancellation_reason"),
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    # ========================================================
    # STEP 1
    # INITIAL USER REQUEST
    # ========================================================

    print_separator(
        "STEP 1 - INITIAL REQUEST"
    )

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
    # STEP 2
    # LOCATION
    # ========================================================

    print_separator(
        "STEP 2 - PROVIDE LOCATION"
    )

    location = {
        "latitude": 13.0827,
        "longitude": 80.2707,
    }

    print(
        "User:",
        location,
    )

    result = await app_graph.ainvoke(
        Command(
            resume=location
        ),
        config=config,
    )

    print_interrupts(result)

    # ========================================================
    # STEP 3
    # TIME
    # ========================================================

    print_separator(
        "STEP 3 - PROVIDE TIME"
    )

    user_time = "tomorrow at 6 AM"

    print(
        "User:",
        user_time,
    )

    result = await app_graph.ainvoke(
        Command(
            resume=user_time
        ),
        config=config,
    )

    print_interrupts(result)

    # ========================================================
    # STEP 4
    # PFZ SELECTION
    # ========================================================

    print_separator(
        "STEP 4 - SELECT PFZ"
    )

    interrupts = result.get(
        "__interrupt__"
    )

    # --------------------------------------------------------
    # Make sure an interrupt exists
    # --------------------------------------------------------

    if not interrupts:

        print(
            "❌ No interrupt returned after time."
        )

        print_state(result)

        return

    # --------------------------------------------------------
    # Read interrupt
    # --------------------------------------------------------

    interrupt_value = interrupts[0].value

    action = interrupt_value.get(
        "action"
    )

    print(
        "Pending action:",
        action,
    )

    # --------------------------------------------------------
    # Verify PFZ selection
    # --------------------------------------------------------

    if action != "SELECT_PFZ":

        print(
            "❌ Expected SELECT_PFZ."
        )

        print_state(result)

        return

    # --------------------------------------------------------
    # Get PFZ options
    # --------------------------------------------------------

    options = interrupt_value.get(
        "options",
        [],
    )

    print(
        "\nAvailable PFZs:"
    )

    for index, option in enumerate(
        options,
        start=1,
    ):

        # ----------------------------------------------------
        # String option
        # ----------------------------------------------------

        if isinstance(
            option,
            str,
        ):

            print(
                f"{index}. {option}"
            )

        # ----------------------------------------------------
        # Dictionary option
        # ----------------------------------------------------

        elif isinstance(
            option,
            dict,
        ):

            pfz_name = option.get(
                "pfz_name"
            )

            times = option.get(
                "times",
                [],
            )

            if times:

                time_info = times[0]

                if isinstance(
                    time_info,
                    dict,
                ):

                    print(
                        f"{index}. {pfz_name} | "
                        f"Risk: "
                        f"{time_info.get('risk_score')} | "
                        f"Level: "
                        f"{time_info.get('risk_level')} | "
                        f"Time: "
                        f"{time_info.get('time')}"
                    )

                else:

                    print(
                        f"{index}. "
                        f"{pfz_name} | "
                        f"Time: {time_info}"
                    )

            else:

                print(
                    f"{index}. "
                    f"{pfz_name}"
                )

        # ----------------------------------------------------
        # Unknown option
        # ----------------------------------------------------

        else:

            print(
                f"{index}. {option}"
            )

    # ========================================================
    # SELECT PFZ
    # ========================================================

    selected_pfz = (
        "Kanathur Reddy Kuppam"
    )

    print(
        "\nUser selected:",
        selected_pfz,
    )

    # --------------------------------------------------------
    # Resume graph
    # --------------------------------------------------------

    result = await app_graph.ainvoke(
        Command(
            resume=selected_pfz
        ),
        config=config,
    )

    print_interrupts(result)

    # ========================================================
    # STEP 5
    # FINAL RESULT
    # ========================================================

    print_separator(
        "STEP 5 - FINAL RESULT"
    )

    print_state(result)

    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    print_separator(
        "FINAL VALIDATION"
    )

    selected_name = result.get(
        "selected_pfz_name"
    )

    route_result = result.get(
        "route_result"
    )

    response = result.get(
        "response"
    )

    workflow_status = result.get(
        "workflow_status"
    )

    interrupts = result.get(
        "__interrupt__"
    )

    print(
        "Workflow status :",
        workflow_status,
    )

    print(
        "Selected PFZ    :",
        selected_name,
    )

    print(
        "Route result    :",
        "✅ EXISTS"
        if route_result
        else "❌ MISSING",
    )

    print(
        "Response        :",
        "✅ EXISTS"
        if response
        else "❌ MISSING",
    )

    print(
        "Interrupt       :",
        "⏸️ WAITING"
        if interrupts
        else "✅ NONE",
    )

    # ========================================================
    # SUCCESS
    # ========================================================

    if (
        selected_name
        and route_result
        and response
        and not interrupts
    ):

        print(
            "\n🎉 FULL PLANNING FLOW COMPLETED!"
        )

    # ========================================================
    # PARTIAL SUCCESS
    # ========================================================

    elif selected_name and route_result:

        print(
            "\n✅ PFZ + ROUTE completed."
        )

        if interrupts:

            print(
                "⚠️ Graph is still waiting "
                "for another input."
            )

        if not response:

            print(
                "⚠️ Final response is missing."
            )

    # ========================================================
    # FAILURE
    # ========================================================

    else:

        print(
            "\n❌ FULL FLOW DID NOT COMPLETE."
        )

        print_state(result)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())