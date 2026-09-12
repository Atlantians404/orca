import asyncio

from ai.agent_state import AgentState
from ai.schemas.location import Location
from ai.schemas.time import TimeContext

from ai.graph.nodes import route_node


def make_time_context():
    return TimeContext(
        slots=[
            {
                "date": "2026-09-13",
                "start_time": "08:00",
                "end_time": None,
            }
        ]
    )


async def main():

    print("\n" + "=" * 70)
    print("ROUTE ENGINE INTEGRATION TEST")
    print("=" * 70)

    state: AgentState = {
        "location": Location(
            place="Chennai",
            latitude=13.0827,
            longitude=80.2707,
        ),

        "time_context": make_time_context(),

        "selected_pfz_name": "PFZ Zone 1",

        "selected_pfz": {
            "name": "PFZ Zone 1",
            "latitude": 13.371389,
            "longitude": 80.434167,
        },

        "route_required": True,
    }

    print("\n" + "=" * 70)
    print("STARTING ROUTE NODE")
    print("=" * 70)

    result = await route_node(state)

    route_result = result.get("route_result")

    if not route_result:
        print("\n❌ Route Engine did not produce route_result")
        return

    print("\n" + "=" * 70)
    print("ROUTE RESULT")
    print("=" * 70)

    print(
        "\nCoastal Reference:",
        route_result.get("coastal_reference"),
    )

    candidate_routes = route_result.get(
        "candidate_routes",
        [],
    )

    print(
        "\nCandidate Routes:",
        len(candidate_routes),
    )

    for route in candidate_routes:

        print("\nRoute:", route["route_id"])
        print(
            "Distance:",
            route["distance_km"],
            "km",
        )
        print(
            "Risk Score:",
            route["risk_score"],
        )
        print(
            "Safe:",
            route["safe"],
        )
        print(
            "Waypoints:",
            len(route["waypoints"]),
        )

    safe_route = route_result.get(
        "safe_route"
    )

    print("\n" + "=" * 70)
    print("SAFE ROUTE")
    print("=" * 70)

    if safe_route:
        print(
            "\nRoute ID:",
            safe_route["route_id"],
        )
        print(
            "Distance:",
            safe_route["distance_km"],
            "km",
        )
        print(
            "Risk Score:",
            safe_route["risk_score"],
        )
        print(
            "Safe:",
            safe_route["safe"],
        )

    else:
        print("\n⚠️ No safe route found")

    print("\n" + "=" * 70)
    print("ROUTE RISK RESULT")
    print("=" * 70)

    print(result.get("risk_result"))

    print("\n" + "=" * 70)
    print("RUNNING ASSERTIONS")
    print("=" * 70)

    assert result.get("route_result") is not None
    print("✅ route_result exists")

    assert "candidate_routes" in route_result
    print("✅ candidate_routes exists")

    assert len(candidate_routes) <= 3
    print("✅ Maximum 3 candidate routes")

    assert "safe_route" in route_result
    print("✅ safe_route exists")

    assert result.get("risk_result") is not None
    print("✅ route risk_result exists")

    assert "routes" in result["risk_result"]
    print("✅ route risk results exist")

    assert result["risk_result"]["selected_route_id"] == (
        safe_route["route_id"]
        if safe_route
        else None
    )
    print("✅ selected_route_id is correct")

    print("\n" + "=" * 70)
    print("✅ ROUTE ENGINE INTEGRATION TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())