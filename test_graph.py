import asyncio
import json

from ai.orchestrator import orchestrate


TEST_CASES = [
    # ========================================================
    # LOCATION + TIME
    # ========================================================

    "I want to fish around Mahabalipuram tomorrow evening",

    "Plan a fishing trip from Chennai tomorrow morning",

    "I want to go fishing around Cuddalore at 6 AM tomorrow",

    "I want to fish from Pondicherry at 5:30 PM",

    # ========================================================
    # LOCATION ONLY
    # ========================================================

    "I want to fish around Mahabalipuram",

    "Plan a fishing trip from Chennai",

    "I want to go fishing from Cuddalore",

    # ========================================================
    # TIME ONLY
    # ========================================================

    "I want to go fishing tomorrow evening",

    "Plan a fishing trip tomorrow at 6 AM",

    "I want to leave at 17:30",

    # ========================================================
    # COORDINATES
    # ========================================================

    "I want to fish at 12.85, 80.28 tomorrow morning",

    "Plan fishing from 12.779167, 80.342222 at 6 PM",

    # ========================================================
    # DISTANCE
    # ========================================================

    "Find a PFZ within 20 km from Mahabalipuram tomorrow morning",

    "Find fishing zones within 30 kilometers from Chennai",

    # ========================================================
    # PFZ / SAFETY
    # ========================================================

    "Is Pondicherry safe for fishing?",

    "Is Nagapattinam Harbour safe?",

    "Is Kanathur Reddy Kuppam safe tomorrow evening?",

    # ========================================================
    # ROUTE
    # ========================================================

    "Give me a route to Pondicherry",

    "Find the safest route to Kanathur Reddy Kuppam",

    "How do I reach the selected PFZ tomorrow morning?",

    # ========================================================
    # GENERAL
    # ========================================================

    "What is a PFZ?",

    "What does PFZ mean?",

    "What is the weather like for fishing?",
]


async def run_test(prompt: str):

    print("\n" + "=" * 80)
    print(f"INPUT: {prompt}")
    print("=" * 80)

    state = {
        "prompt": prompt,
        "workflow_status": "IN_PROGRESS",
    }

    try:

        result = await orchestrate(state)

        print(
            json.dumps(
                result,
                indent=4,
                default=str,
            )
        )

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        assert result["query_type"] in {
            "general",
            "safety",
            "planning",
        }

        assert (
            "location" in result
        )

        assert (
            "time_context" in result
        )

        assert (
            "distance_km" in result
        )

        assert (
            "selected_pfz_name" in result
        )

        assert (
            "route_required" in result
        )

        print("\n✅ STRUCTURE OK")

        # ----------------------------------------------------
        # Location validation
        # ----------------------------------------------------

        location = result.get(
            "location"
        )

        if location:

            print(
                "\n📍 LOCATION:"
            )

            print(
                f"   place      = {location.place}"
            )

            print(
                f"   latitude   = {location.latitude}"
            )

            print(
                f"   longitude  = {location.longitude}"
            )

        else:

            print(
                "\n📍 LOCATION: None"
            )

        # ----------------------------------------------------
        # Time validation
        # ----------------------------------------------------

        time_context = result.get(
            "time_context"
        )

        if time_context:

            print(
                "\n🕐 TIME:"
            )

            print(
                f"   timezone = {time_context.timezone}"
            )

            for slot in time_context.slots:

                print(
                    f"   date       = {slot.date}"
                )

                print(
                    f"   start_time = {slot.start_time}"
                )

                print(
                    f"   end_time   = {slot.end_time}"
                )

        else:

            print(
                "\n🕐 TIME: None"
            )

        # ----------------------------------------------------
        # Other fields
        # ----------------------------------------------------

        print(
            "\n📋 OTHER:"
        )

        print(
            f"   query_type        = {result.get('query_type')}"
        )

        print(
            f"   distance_km       = {result.get('distance_km')}"
        )

        print(
            f"   selected_pfz_name = {result.get('selected_pfz_name')}"
        )

        print(
            f"   route_required    = {result.get('route_required')}"
        )

    except Exception as exc:

        print(
            f"\n❌ TEST FAILED: {type(exc).__name__}"
        )

        print(
            f"   {exc}"
        )


async def main():

    for prompt in TEST_CASES:

        await run_test(prompt)


if __name__ == "__main__":
    asyncio.run(main())
