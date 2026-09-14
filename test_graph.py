import asyncio
import json

from ai.graph.graph import app_graph


TEST_CASES = [
    "I want to fish from Pondicherry at 5:30 PM",
    "I want to leave at 17:30",
    "Plan fishing from 12.779167, 80.342222 at 6 PM",
]


async def run_test(prompt: str):
    print("\n" + "=" * 80)
    print(f"PROMPT: {prompt}")
    print("=" * 80)

    thread_id = f"test-{abs(hash(prompt))}"

    initial_state = {
        "thread_id": thread_id,
        "prompt": prompt,
        "workflow_status": "IN_PROGRESS",
        "route_required": False,
    }

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    try:
        result = await app_graph.ainvoke(
            initial_state,
            config=config,
        )

        print("\nRESULT:")

        print(
            json.dumps(
                {
                    "query_type": result.get("query_type"),
                    "location": (
                        result["location"].model_dump()
                        if result.get("location")
                        and hasattr(result["location"], "model_dump")
                        else result.get("location")
                    ),
                    "time_context": (
                        result["time_context"].model_dump()
                        if result.get("time_context")
                        and hasattr(result["time_context"], "model_dump")
                        else result.get("time_context")
                    ),
                    "workflow_status": result.get("workflow_status"),
                    "error_message": result.get("error_message"),
                },
                indent=2,
                default=str,
            )
        )

    except Exception as exc:
        print("\nERROR:")
        print(type(exc).__name__, str(exc))


async def main():
    for prompt in TEST_CASES:
        await run_test(prompt)


if __name__ == "__main__":
    asyncio.run(main())