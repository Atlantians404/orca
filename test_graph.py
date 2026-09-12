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
    print(json.dumps(result, indent=2, default=str))

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
    print(json.dumps(result, indent=2, default=str))

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
    print(json.dumps(result, indent=2, default=str))

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

    print("\n[STEP 4] FINAL GRAPH RESPONSE:")
    print(json.dumps(result, indent=2, default=str))

    # ============================================================
    # STEP 5 — Inspect final state
    # ============================================================

    print("\n" + "=" * 70)
    print("FINAL STATE INSPECTION")
    print("=" * 70)

    final_state = await graph.aget_state(config)

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
        f"CANDIDATE ROUTES: {len(candidate_routes)}"
    )
    print("=" * 70)

    for route in candidate_routes:

        print("\nRoute:")
        print(
            f"  ID: {route.get('route_id')}"
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

        waypoints = route.get(
            "waypoints",
            [],
        )

        print(
            f"  Waypoints: "
            f"{len(waypoints)}"
        )

        print(
            "  GeoJSON: "
            + (
                "YES"
                if route.get("geojson")
                else "NO"
            )
        )

        nodes = route.get(
            "nodes",
            [],
        )

        print(
            f"  Risk nodes: "
            f"{len(nodes)}"
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

        print(
            f"Waypoints: "
            f"{len(safe_route.get('waypoints', []))}"
        )

        print(
            "GeoJSON: "
            + (
                "YES"
                if safe_route.get("geojson")
                else "NO"
            )
        )

    else:
        print("⚠️ No safe route was found.")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())