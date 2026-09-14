import asyncio

from langgraph.types import Command

from ai.graph.graph import build_graph


async def test_graph():

    # ------------------------------------------------------------
    # Build graph
    # ------------------------------------------------------------

    graph = build_graph()

    session_id = "graph-route-test-001"

    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

<<<<<<< HEAD
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
=======
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
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f
        },
        config=config,
    )

<<<<<<< HEAD
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
=======
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
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f

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

<<<<<<< HEAD
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
=======
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
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f

    fishing_time = "tomorrow at 6 AM"

    print("User:", fishing_time)

    result = await graph.ainvoke(
        Command(
            resume=fishing_time
        ),
        config=config,
    )

<<<<<<< HEAD
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
=======
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
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f

    selected_pfz_name = "Kanathur Reddy Kuppam"

    print("User selected:", selected_pfz_name)

    result = await graph.ainvoke(
        Command(
<<<<<<< HEAD
            resume=selected_pfz_name
=======
            resume="Kanathur Reddy Kuppam"
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f
        ),
        config=config,
    )

<<<<<<< HEAD
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
=======
    print("Pending action:")
    print(result.get("pending_action"))

    print("Workflow status:")
    print(result.get("workflow_status"))
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f

    print("\nRoute required:")
    print(result.get("route_required"))

<<<<<<< HEAD
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
=======
    # =========================================================
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f
    # ROUTE RESULT
    # =========================================================

<<<<<<< HEAD
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
=======
    print("\n========== ROUTE RESULT ==========")

    route_result = result.get("route_result")
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f

    if route_result is None:
        print("❌ route_result = None")
    else:
        print("✅ route_result exists")

        print("\nRoute result:")
        print(route_result)

<<<<<<< HEAD
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
=======
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
>>>>>>> 479652e453fc0229fd9753d7fa899567fc40351f
