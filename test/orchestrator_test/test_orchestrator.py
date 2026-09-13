import pytest

from ai.orchestrator import orchestrate


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "prompt, expected",
    [
        # General
        ("What is the weather today?", "general"),
        ("What is the sea temperature?", "general"),
        ("What are the current marine conditions?", "general"),
        ("Tell me about fishing conditions.", "general"),
        ("What does PFZ mean?", "general"),

        # Safety
        ("Is PFZ03 safe tomorrow at 5 PM?", "safety"),
        ("What is the risk level of PFZ05?", "safety"),
        ("Is PFZ10 safe for fishing?", "safety"),
        ("Can I fish at PFZ02 tomorrow morning?", "safety"),
        ("Check the safety of PFZ07 at 6 PM.", "safety"),

        # Planning
        (
            "Tomorrow I want to go fishing. Find me a safe PFZ.",
            "planning",
        ),
        (
            "Find a good PFZ for fishing tomorrow.",
            "planning",
        ),
        (
            "Recommend a safe fishing zone near my location.",
            "planning",
        ),
        (
            "Plan my fishing trip for tomorrow.",
            "planning",
        ),
        (
            "Find the best PFZ within 30 km.",
            "planning",
        ),
        (
            "I want to go fishing at 5 PM. Find a suitable PFZ.",
            "planning",
        ),
        (
            "Find me a safe PFZ and give me a route.",
            "planning",
        ),
        (
            "I'm going fishing tomorrow from Chennai. What PFZ should I choose?",
            "planning",
        ),
        (
            "Find 5 suitable PFZ zones for tomorrow evening.",
            "planning",
        ),
        (
            "I want to plan a fishing trip and need the safest PFZ.",
            "planning",
        ),
    ],
)
async def test_orchestrator_query_type(prompt, expected):

    state = {
        "prompt": prompt
    }

    result = await orchestrate(state)

    assert result["query_type"] == expected


@pytest.mark.asyncio
async def test_orchestrator_extracts_pfz():

    state = {
        "prompt": "Is PFZ03 safe tomorrow at 5 PM?"
    }

    result = await orchestrate(state)

    assert result["query_type"] == "safety"
    assert result["selected_pfz_id"] == "PFZ03"
    assert result["distance_km"] is None
    assert result["route_required"] is False


@pytest.mark.asyncio
async def test_orchestrator_extracts_distance():

    state = {
        "prompt": "Find a safe PFZ within 20 km."
    }

    result = await orchestrate(state)

    assert result["query_type"] == "planning"
    assert result["distance_km"] == 20
    assert result["selected_pfz_id"] is None
    assert result["route_required"] is False


@pytest.mark.asyncio
async def test_orchestrator_extracts_route_and_pfz():

    state = {
        "prompt": "Give me a safe route to PFZ07."
    }

    result = await orchestrate(state)

    assert result["query_type"] == "planning"
    assert result["selected_pfz_id"] == "PFZ07"
    assert result["route_required"] is True