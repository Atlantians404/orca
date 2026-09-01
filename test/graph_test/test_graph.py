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

    result = await app_graph.ainvoke({
        "prompt": prompt
    })

    print(f"\nPrompt: {prompt}")
    print(f"Query Type: {result['query_type']}")
    print(f"Response: {result['response']}")
    print(f"Status: {result['workflow_status']}")

    assert result["query_type"] == expected
    assert result["workflow_status"] == "COMPLETED"