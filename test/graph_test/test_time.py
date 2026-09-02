import pytest

from langgraph.types import Command

from ai.graph.nodes import time_node
from ai.graph.graph import app_graph

from ai.schemas.location import Location
from ai.schemas.time import TimeContext, TimeSlot


@pytest.mark.asyncio
async def test_time_exists():

    time_context = TimeContext(
        slots=[
            TimeSlot(
                date="2026-09-03",
                start_time="17:00"
            )
        ]
    )

    state = {
        "time_context": time_context
    }

    result = await time_node(state)

    assert result["time_context"] == time_context
    assert result["workflow_status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_time_hitl_resume_specific():

    config = {
        "configurable": {
            "thread_id": "test-time-specific"
        }
    }

    result = await app_graph.ainvoke(
        {
            "prompt": "Plan my fishing trip tomorrow.",
            "location": Location(
                place="Chennai",
                latitude=13.0827,
                longitude=80.2707,
            ),
        },
        config=config,
    )

    # Graph should pause at time_node
    assert "__interrupt__" in result

    interrupt_data = result["__interrupt__"][0].value

    assert interrupt_data["action"] == "GET_TIME"

    # Resume with specific time
    result = await app_graph.ainvoke(
        Command(
            resume="tomorrow at 5 PM"
        ),
        config=config,
    )

    time_context = result["time_context"]

    assert time_context is not None
    assert len(time_context.slots) == 1

    assert time_context.slots[0].start_time == "17:00"


@pytest.mark.asyncio
async def test_time_hitl_resume_generic():

    config = {
        "configurable": {
            "thread_id": "test-time-generic"
        }
    }

    result = await app_graph.ainvoke(
        {
            "prompt": "Plan my fishing trip tomorrow.",
            "location": Location(
                place="Chennai",
                latitude=13.0827,
                longitude=80.2707,
            ),
        },
        config=config,
    )

    # Graph should pause at time_node
    assert "__interrupt__" in result

    interrupt_data = result["__interrupt__"][0].value

    assert interrupt_data["action"] == "GET_TIME"

    # Resume with generic time
    result = await app_graph.ainvoke(
        Command(
            resume="tomorrow morning"
        ),
        config=config,
    )

    time_context = result["time_context"]

    assert time_context is not None

    # Generic time should create 3 slots
    assert len(time_context.slots) == 3

    assert time_context.slots[0].start_time == "06:00"
    assert time_context.slots[0].end_time == "09:00"

    assert time_context.slots[1].start_time == "09:00"
    assert time_context.slots[1].end_time == "12:00"

    assert time_context.slots[2].start_time == "12:00"
    assert time_context.slots[2].end_time == "15:00"

    assert time_context.timezone == "Asia/Kolkata"