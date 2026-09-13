import asyncio
import json

from langgraph.types import Command

from ai.graph.graph import build_graph


SESSION_ID = "test-route-flow-001"


async def main():

    print("\n" + "=" * 70)
    print("ORCA FULL ROUTE FLOW TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # Build graph
    # ------------------------------------------------------------

    graph = build_graph()

    config = {
        "configurable": {
            "thread_id": SESSION_ID
        }
    }

    # ============================================================
    # STEP 1
    # Initial user request
    # ============================================================

    print("\n" + "-" * 70)
    print("[STEP 1] Initial request")
    print("-" * 70)

    print("User: Plan a Trip with route")

    result = await graph.ainvoke(
        {
            "prompt": "Plan a Trip with route"
        },
        config=config,
    )

    print("\nGraph response:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # STEP 2
    # Provide location
    # ============================================================

    print("\n" + "-" * 70)
    print("[STEP 2] Providing location")
    print("-" * 70)

    location = {
        "latitude": 13.0827,
        "longitude": 80.2707,
    }

    print("User:", location)

    result = await graph.ainvoke(
        Command(
            resume=location
        ),
        config=config,
    )

    print("\nGraph response:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # STEP 3
    # Provide fishing time
    # ============================================================

    print("\n" + "-" * 70)
    print("[STEP 3] Providing fishing time")
    print("-" * 70)

    fishing_time = "tomorrow at 6 AM"

    print("User:", fishing_time)

    result = await graph.ainvoke(
        Command(
            resume=fishing_time
        ),
        config=config,
    )

    print("\nGraph response:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # STEP 4
    # Select PFZ
    #
    # IMPORTANT:
    # This must match one of the PFZ names returned by the
    # risk engine.
    # ============================================================

    print("\n" + "-" * 70)
    print("[STEP 4] Selecting PFZ")
    print("-" * 70)

    selected_pfz_name = "Kanathur Reddy Kuppam"

    print("User selected:", selected_pfz_name)

    result = await graph.ainvoke(
        Command(
            resume=selected_pfz_name
        ),
        config=config,
    )

    print("\nGraph response:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # DEBUG
    # Inspect state immediately after PFZ selection
    # ============================================================

    state_after_selection = await graph.aget_state(
        config
    )

    print("\n" + "=" * 70)
    print("STATE AFTER PFZ SELECTION")
    print("=" * 70)

    state_values = state_after_selection.values

    debug_state = {
        "selected_pfz_name": state_values.get(
            "selected_pfz_name"
        ),
        "selected_pfz": state_values.get(
            "selected_pfz"
        ),
        "route_required": state_values.get(
            "route_required"
        ),
        "pending_action": state_values.get(
            "pending_action"
        ),
        "workflow_status": state_values.get(
            "workflow_status"
        ),
    }

    print(
        json.dumps(
            debug_state,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # Verify PFZ selection
    # ============================================================

    print("\n" + "=" * 70)
    print("PFZ SELECTION CHECK")
    print("=" * 70)

    selected_pfz = state_values.get(
        "selected_pfz"
    )

    selected_pfz_name_state = state_values.get(
        "selected_pfz_name"
    )

    if selected_pfz:

        print("✅ selected_pfz exists")

        print(
            json.dumps(
                selected_pfz,
                indent=2,
                default=str,
            )
        )

    else:

        print("❌ selected_pfz is missing")

    if selected_pfz_name_state:

        print(
            f"✅ selected_pfz_name: "
            f"{selected_pfz_name_state}"
        )

    else:

        print("❌ selected_pfz_name is missing")

    # ============================================================
    # FULL STATE AFTER SELECTION
    # ============================================================

    print("\n" + "=" * 70)
    print("FULL STATE AFTER PFZ SELECTION")
    print("=" * 70)

    print(
        json.dumps(
            state_values,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # STEP 5
    # Get final state
    # ============================================================

    print("\n" + "=" * 70)
    print("[STEP 5] FINAL STATE")
    print("=" * 70)

    final_state = await graph.aget_state(
        config
    )

    final_values = final_state.values

    print(
        json.dumps(
            final_values,
            indent=2,
            default=str,
        )
    )

    # ============================================================
    # ROUTE RESULT
    # ============================================================

    route_result = final_values.get(
        "route_result"
    )

    print("\n" + "=" * 70)
    print("ROUTE RESULT")
    print("=" * 70)

    if route_result is None:

        print("❌ route_result is missing")

    else:

        print(
            json.dumps(
                route_result,
                indent=2,
                default=str,
            )
        )

    # ============================================================
    # ROUTE ERROR
    # ============================================================

    if route_result:

        route_error = route_result.get(
            "error"
        )

        if route_error:

            print("\n" + "=" * 70)
            print("ROUTE ERROR")
            print("=" * 70)

            print(
                f"❌ {route_error}"
            )

    # ============================================================
    # CANDIDATE ROUTES
    # ============================================================

    candidate_routes = []

    if route_result:

        candidate_routes = route_result.get(
            "candidate_routes",
            []
        )

    print("\n" + "=" * 70)
    print(
        f"CANDIDATE ROUTES: "
        f"{len(candidate_routes)}"
    )
    print("=" * 70)

    for index, route in enumerate(
        candidate_routes,
        start=1,
    ):

        print("\n" + "-" * 50)
        print(f"ROUTE {index}")
        print("-" * 50)

        print(
            "Route ID:",
            route.get("route_id"),
        )

        print(
            "Distance:",
            route.get("distance_km"),
            "km",
        )

        print(
            "Risk Score:",
            route.get("risk_score"),
        )

        print(
            "Safe:",
            route.get("safe"),
        )

        # --------------------------------------------------------
        # Waypoints
        # --------------------------------------------------------

        waypoints = route.get(
            "waypoints",
            []
        )

        print(
            "Waypoints:",
            len(waypoints),
        )

        for waypoint_index, waypoint in enumerate(
            waypoints,
            start=1,
        ):

            print(
                f"  {waypoint_index}. "
                f"{waypoint.get('latitude')}, "
                f"{waypoint.get('longitude')}"
            )

        # --------------------------------------------------------
        # GeoJSON
        # --------------------------------------------------------

        geojson = route.get(
            "geojson"
        )

        print(
            "GeoJSON:",
            "YES" if geojson else "NO",
        )

        # --------------------------------------------------------
        # Risk nodes
        # --------------------------------------------------------

        nodes = route.get(
            "nodes",
            []
        )

        print(
            "Risk nodes:",
            len(nodes),
        )

        for node_index, node in enumerate(
            nodes,
            start=1,
        ):

            print(
                f"  {node_index}. "
                f"{node.get('latitude')}, "
                f"{node.get('longitude')} "
                f"→ risk={node.get('risk_score')} "
                f"safe={node.get('safe')}"
            )

    # ============================================================
    # SAFE ROUTE
    # ============================================================

    safe_route = None

    if route_result:

        safe_route = route_result.get(
            "safe_route"
        )

    print("\n" + "=" * 70)
    print("SAFE ROUTE")
    print("=" * 70)

    if safe_route:

        print(
            "Route ID:",
            safe_route.get("route_id"),
        )

        print(
            "Distance:",
            safe_route.get("distance_km"),
            "km",
        )

        print(
            "Risk Score:",
            safe_route.get("risk_score"),
        )

        print(
            "Safe:",
            safe_route.get("safe"),
        )

        safe_waypoints = safe_route.get(
            "waypoints",
            []
        )

        print(
            "Waypoints:",
            len(safe_waypoints),
        )

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
            "GeoJSON:",
            "YES"
            if safe_route.get("geojson")
            else "NO",
        )

        safe_nodes = safe_route.get(
            "nodes",
            []
        )

        print(
            "Risk nodes:",
            len(safe_nodes),
        )

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
    # FINAL RESPONSE
    # ============================================================

    response = final_values.get(
        "response"
    )

    print("\n" + "=" * 70)
    print("FINAL RESPONSE")
    print("=" * 70)

    if response:

        print(
            response.get(
                "message",
                "No response message.",
            )
        )

    else:

        print("No final response found.")

    # ============================================================
    # FINAL STATUS
    # ============================================================

    print("\n" + "=" * 70)
    print("FINAL TEST STATUS")
    print("=" * 70)

    print(
        "Selected PFZ:",
        final_values.get(
            "selected_pfz_name"
        ),
    )

    print(
        "Route required:",
        final_values.get(
            "route_required"
        ),
    )

    print(
        "Workflow status:",
        final_values.get(
            "workflow_status"
        ),
    )

    if selected_pfz and route_result:

        if safe_route:

            print(
                "\n✅ FULL ROUTE FLOW SUCCESS"
            )

        elif candidate_routes:

            print(
                "\n⚠️ ROUTES GENERATED, "
                "BUT NO SAFE ROUTE"
            )

        else:

            print(
                "\n⚠️ PFZ SELECTED, "
                "BUT NO ROUTES GENERATED"
            )

    elif not selected_pfz:

        print(
            "\n❌ PFZ SELECTION FAILED"
        )

    else:

        print(
            "\n❌ ROUTE FLOW FAILED"
        )

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())