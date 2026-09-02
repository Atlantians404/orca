import pytest

from ai.graph.nodes import time_node
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
async def test_time_missing():

    state = {}

    result = await time_node(state)

    assert result["pending_action"] == "GET_TIME"
    assert result["workflow_status"] == "WAITING_FOR_USER"