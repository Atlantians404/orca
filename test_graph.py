import asyncio

from langgraph.types import Command

from ai.graph.graph import build_graph


async def test_graph():

    graph = build_graph()

    session_id = "graph-route-test-001"

    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    # =========================================================
    # STEP 1 — Initial request
    # =========================================================

    print("\n========== STEP 1 ==========")

    result = await graph.ainvoke(
        {
            "thread_id": session_id,
            "prompt": "Plan a fishing trip with route",
            "workflow_status": "IN_PROGRESS",
            "route_required": True,
        },
        config=config,
    )

    print("Pending action:")
    print(result.get("pending_action"))

    print("Workflow status:")
    print(result.get("workflow_status"))

    print("Interrupt:")
    print(result.get("__interrupt__"))

    # =========================================================
    # STEP 2 — Location
    # =========================================================

    print("\n========== STEP 2 ==========")

    result = await graph.ainvoke(
        Command(
            resume={
                "latitude": 13.0827,
                "longitude": 80.2707,
            }
        ),
        config=config,
    )

    print("Pending action:")
    print(result.get("pending_action"))

    print("Workflow status:")
    print(result.get("workflow_status"))

    print("Interrupt:")
    print(result.get("__interrupt__"))

    # =========================================================
    # STEP 3 — Time
    # =========================================================

    print("\n========== STEP 3 ==========")

    result = await graph.ainvoke(
        Command(
            resume="tomorrow at 6 AM"
        ),
        config=config,
    )

    print("Pending action:")
    print(result.get("pending_action"))

    print("Workflow status:")
    print(result.get("workflow_status"))

    print("Interrupt:")
    print(result.get("__interrupt__"))

    print("\nRoute required:")
    print(result.get("route_required"))

    # =========================================================
    # STEP 4 — PFZ selection
    # =========================================================

    print("\n========== STEP 4 ==========")

    result = await graph.ainvoke(
        Command(
            resume="Kanathur Reddy Kuppam"
        ),
        config=config,
    )

    print("Pending action:")
    print(result.get("pending_action"))

    print("Workflow status:")
    print(result.get("workflow_status"))

    print("\nRoute required:")
    print(result.get("route_required"))

    # =========================================================
    # ROUTE RESULT
    # =========================================================

    print("\n========== ROUTE RESULT ==========")

    route_result = result.get("route_result")

    if route_result is None:
        print("❌ route_result = None")
    else:
        print("✅ route_result exists")

        print("\nRoute result:")
        print(route_result)

        print("\nSafe route:")
        print(
            route_result.get("safe_route")
        )

        print("\nCandidate routes:")
        candidate_routes = route_result.get(
            "candidate_routes",
            []
        )

        print(
            f"Number of candidates: "
            f"{len(candidate_routes)}"
        )

        for route in candidate_routes:
            print(
                f"\n{route.get('route_id')}"
            )
            print(
                f"Distance: "
                f"{route.get('distance_km')}"
            )
            print(
                f"Risk: "
                f"{route.get('risk_score')}"
            )
            print(
                f"Safe: "
                f"{route.get('safe')}"
            )
            print(
                f"Waypoints: "
                f"{len(route.get('waypoints', []))}"
            )

    # =========================================================
    # FINAL RESPONSE
    # =========================================================

    print("\n========== FINAL RESPONSE ==========")

    response = result.get("response")

    print(response)

    # =========================================================
    # IMPORTANT STATE CHECKS
    # =========================================================

    print("\n========== STATE CHECK ==========")

    print(
        "selected_pfz_name:",
        result.get("selected_pfz_name")
    )

    print(
        "selected_pfz:",
        result.get("selected_pfz")
    )

    print(
        "route_required:",
        result.get("route_required")
    )

    print(
        "route_result exists:",
        result.get("route_result") is not None
    )


if __name__ == "__main__":
    asyncio.run(test_graph())