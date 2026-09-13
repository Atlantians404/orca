import asyncio
import json

from langgraph.types import Command

from ai.graph.graph import build_graph


SESSION_ID = "test-route-flow-001"


async def main():

    print("\n" + "=" * 70)
    print("ORCA FULL ROUTE FLOW TEST")
    print("=" * 70)

    graph = build_graph()

    config = {
        "configurable": {
            "thread_id": SESSION_ID
        }
    }

    # ============================================================
    # STEP 1 — Initial request
    # ============================================================

    print("\n[STEP 1] User:")
    print("Plan a Trip with route")

    result = await graph.ainvoke(
        {
            "prompt": "Plan a Trip with route",
        },
        config=config,
    )

    print("\n[STEP 1] Graph response:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # STEP 2 — Resume GET_LOCATION
    # ============================================================

    print("\n" + "-" * 70)
    print("[STEP 2] Providing location...")
    print("-" * 70)

    result = await graph.ainvoke(
        Command(
            resume={
                "latitude": 13.0827,
                "longitude": 80.2707,
            }
        ),
        config=config,
    )

    print("\n[STEP 2] Graph response:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # STEP 3 — Resume GET_TIME
    # ============================================================

    print("\n" + "-" * 70)
    print("[STEP 3] Providing fishing time...")
    print("-" * 70)

    result = await graph.ainvoke(
        Command(
            resume="tomorrow at 6 AM"
        ),
        config=config,
    )

    print("\n[STEP 3] Graph response:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # STEP 4 — Resume SELECT_PFZ
    # ============================================================

    print("\n" + "-" * 70)
    print("[STEP 4] Selecting PFZ...")
    print("-" * 70)

    result = await graph.ainvoke(
        Command(
            resume="Coromandel"
        ),
        config=config,
    )

    print("\n[STEP 4] Graph response:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # IMPORTANT DEBUG
    # Inspect state immediately after PFZ selection
    # ============================================================

    state_after_selection = await graph.aget_state(
        config
    )

    print("\n" + "=" * 70)
    print("STATE AFTER PFZ SELECTION")
    print("=" * 70)

    state_debug = {
        "selected_pfz_name": (
            state_after_selection.values.get(
                "selected_pfz_name"
            )
        ),

        "selected_pfz": (
            state_after_selection.values.get(
                "selected_pfz"
            )
        ),

        "route_required": (
            state_after_selection.values.get(
                "route_required"
            )
        ),

        "pending_action": (
            state_after_selection.values.get(
                "pending_action"
            )
        ),

        "workflow_status": (
            state_after_selection.values.get(
                "workflow_status"
            )
        ),
    }

    print(
        json.dumps(
            state_debug,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # FULL STATE AFTER PFZ SELECTION
    # ============================================================

    print("\n" + "=" * 70)
    print("FULL STATE AFTER PFZ SELECTION")
    print("=" * 70)

    print(
        json.dumps(
            state_after_selection.values,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # STEP 5 — Final state inspection
    # ============================================================

    print("\n" + "=" * 70)
    print("FINAL STATE INSPECTION")
    print("=" * 70)

    final_state = await graph.aget_state(
        config
    )

    print(
        json.dumps(
            final_state.values,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # ROUTE RESULT
    # ============================================================

    route_result = final_state.values.get(
        "route_result"
    )

    print("\n" + "=" * 70)
    print("ROUTE RESULT")
    print("=" * 70)

    if not route_result:

        print("❌ route_result is missing")

        return

    print(
        json.dumps(
            route_result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # CANDIDATE ROUTES
    # ============================================================

    candidate_routes = route_result.get(
        "candidate_routes",
        [],
    )

    print("\n" + "=" * 70)
    print(
        f"CANDIDATE ROUTES: "
        f"{len(candidate_routes)}"
    )
    print("=" * 70)

    for route in candidate_routes:

        print("\nRoute:")
        print(
            f"  ID: "
            f"{route.get('route_id')}"
        )

        print(
            f"  Distance: "
            f"{route.get('distance_km')} km"
        )

        print(
            f"  Risk: "
            f"{route.get('risk_score')}"
        )

        print(
            f"  Safe: "
            f"{route.get('safe')}"
        )

        # --------------------------------------------------------
        # Waypoints
        # --------------------------------------------------------

        waypoints = route.get(
            "waypoints",
            [],
        )

        print(
            f"  Waypoints: "
            f"{len(waypoints)}"
        )

        if waypoints:

            print("  Waypoint coordinates:")

            for index, waypoint in enumerate(
                waypoints,
                start=1,
            ):

                print(
                    f"    {index}. "
                    f"{waypoint.get('latitude')}, "
                    f"{waypoint.get('longitude')}"
                )

        # --------------------------------------------------------
        # GeoJSON
        # --------------------------------------------------------

        print(
            "  GeoJSON: "
            + (
                "YES"
                if route.get("geojson")
                else "NO"
            )
        )

        # --------------------------------------------------------
        # Risk nodes
        # --------------------------------------------------------

        nodes = route.get(
            "nodes",
            [],
        )

        print(
            f"  Risk nodes: "
            f"{len(nodes)}"
        )

        if nodes:

            print("  Waypoint risks:")

            for index, node in enumerate(
                nodes,
                start=1,
            ):

                print(
                    f"    {index}. "
                    f"{node.get('latitude')}, "
                    f"{node.get('longitude')} "
                    f"→ risk={node.get('risk_score')} "
                    f"safe={node.get('safe')}"
                )

    # ============================================================
    # SAFE ROUTE
    # ============================================================

    safe_route = route_result.get(
        "safe_route"
    )

    print("\n" + "=" * 70)
    print("SAFE ROUTE")
    print("=" * 70)

    if safe_route:

        print(
            f"Route ID: "
            f"{safe_route.get('route_id')}"
        )

        print(
            f"Distance: "
            f"{safe_route.get('distance_km')} km"
        )

        print(
            f"Risk Score: "
            f"{safe_route.get('risk_score')}"
        )

        print(
            f"Safe: "
            f"{safe_route.get('safe')}"
        )

        safe_waypoints = safe_route.get(
            "waypoints",
            [],
        )

        print(
            f"Waypoints: "
            f"{len(safe_waypoints)}"
        )

        if safe_waypoints:

            print("Waypoint coordinates:")

            for index, waypoint in enumerate(
                safe_waypoints,
                start=1,
            ):

                print(
                    f"  {index}. "
                    f"{waypoint.get('latitude')}, "
                    f"{waypoint.get('longitude')}"
                )

        print(
            "GeoJSON: "
            + (
                "YES"
                if safe_route.get("geojson")
                else "NO"
            )
        )

        safe_nodes = safe_route.get(
            "nodes",
            [],
        )

        print(
            f"Risk nodes: "
            f"{len(safe_nodes)}"
        )

        if safe_nodes:

            print("Waypoint risks:")

            for index, node in enumerate(
                safe_nodes,
                start=1,
            ):

                print(
                    f"  {index}. "
                    f"{node.get('latitude')}, "
                    f"{node.get('longitude')} "
                    f"→ risk={node.get('risk_score')} "
                    f"safe={node.get('safe')}"
                )

    else:

        print("⚠️ No safe route was found.")

    # ============================================================
    # FINAL TEST STATUS
    # ============================================================

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

