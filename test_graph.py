import asyncio
import json

from ai.orchestrator import orchestrate


TEST_CASES = [
    "Hello",
    "Plan a fishing trip tomorrow at 6 AM from Chennai",
    "Find a safe PFZ within 30 km tomorrow at 6 AM",
    "Is Pondicherry safe?",
    "Give me a route to Pondicherry",
    "I want to go fishing at 5:30 PM",
]


async def test_orchestrator():

    for i, prompt in enumerate(TEST_CASES, 1):

        print("\n" + "=" * 70)
        print(f"TEST {i}")
        print(f"USER: {prompt}")
        print("=" * 70)

        state = {
            "prompt": prompt,
            "conversation_summary": "",
            "workflow_status": "IN_PROGRESS",
        }

        try:

            result = await orchestrate(state)

            print("\nRESULT:")
            print(
                json.dumps(
                    result,
                    indent=4,
                    default=str,
                )
            )

            print("\nSTATUS: ✅ PASSED")

        except Exception as exc:

            print("\nSTATUS: ❌ FAILED")
            print(f"ERROR: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(test_orchestrator())