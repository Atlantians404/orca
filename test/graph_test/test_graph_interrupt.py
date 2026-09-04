import pytest

from langgraph.types import Command

from ai.graph.graph import app_graph


@pytest.mark.asyncio
async def test_planning_location_time_interrupt_resume():

    config = {
        "configurable": {
            "thread_id": "test-planning-location-time"
        }
    }

    # --------------------------------------------------
    # STEP 1
    # Start planning request without location/time
    # --------------------------------------------------

    result = await app_graph.ainvoke(
        {
            "prompt": "Plan my fishing trip tomorrow."
        },
        config=config,
    )

    print("\nSTEP 1 - LOCATION INTERRUPT")
    print(result)

    # Graph should pause at location_node
    assert "__interrupt__" in result

    interrupt_data = result["__interrupt__"][0].value

    assert interrupt_data["action"] == "GET_LOCATION"

    # --------------------------------------------------
    # STEP 2
    # Resume with location
    # --------------------------------------------------

    result = await app_graph.ainvoke(
        Command(
            resume={
                "place": "Chennai",
                "latitude": 13.0827,
                "longitude": 80.2707,
            }
        ),
        config=config,
    )

    print("\nSTEP 2 - TIME INTERRUPT")
    print(result)

    # Location is resolved.
    # Graph should now pause at time_node.
    assert "__interrupt__" in result

    interrupt_data = result["__interrupt__"][0].value

    assert interrupt_data["action"] == "GET_TIME"

    # --------------------------------------------------
    # STEP 3
    # Resume with specific time
    # --------------------------------------------------

    result = await app_graph.ainvoke(
        Command(
            resume="tomorrow at 5 PM"
        ),
        config=config,
    )

    print("\nSTEP 3 - PFZ RESULT")
    print(result)

    # --------------------------------------------------
    # Verify location
    # --------------------------------------------------

    assert result["location"] is not None

    location = result["location"]

    assert location.latitude == 13.0827
    assert location.longitude == 80.2707

    # --------------------------------------------------
    # Verify time
    # --------------------------------------------------

    assert result["time_context"] is not None
    assert len(result["time_context"].slots) == 1

    assert (
        result["time_context"].slots[0].start_time
        == "17:00"
    )

    # --------------------------------------------------
    # Verify PFZ stage was reached
    # --------------------------------------------------

    assert (
        "pfz_candidates" in result
        or "selected_pfz" in result
        or result["workflow_status"] == "COMPLETED"
    )