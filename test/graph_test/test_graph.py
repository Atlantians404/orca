import pytest

from ai.graph.graph import app_graph


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "prompt, expected",
    [
        ("What is the weather today?", "general"),
        ("What is the sea temperature?", "general"),
        ("Is PFZ03 safe tomorrow?", "safety"),
        ("What is the risk level of PFZ05?", "safety"),
        ("Find me a safe PFZ tomorrow.", "planning"),
        ("Plan my fishing trip tomorrow.", "planning"),
    ],
)
async def test_graph_routing(prompt, expected):

    config = {
        "configurable": {
            "thread_id": f"test-{prompt}"
        }
    }

    result = await app_graph.ainvoke(
        {
            "prompt": prompt
        },
        config=config
    )

    print(f"\nPrompt: {prompt}")
    print(f"Query Type: {result.get('query_type')}")
    print(f"Response: {result.get('response')}")
    print(f"Status: {result.get('workflow_status')}")
    print(f"Interrupt: {result.get('__interrupt__')}")

    # Orchestrator should classify correctly
    assert result["query_type"] == expected

    # General requests complete immediately.
    # Safety/planning may pause for Location/Time HITL.
    assert (
        result.get("workflow_status") == "COMPLETED"
        or "__interrupt__" in result
    )