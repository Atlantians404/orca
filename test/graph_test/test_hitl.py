import pytest

from langgraph.types import Command

from ai.graph.graph import app_graph


@pytest.mark.asyncio
async def test_location_and_time_hitl_resume():

    config = {
        "configurable": {
            "thread_id": "test-location-time-hitl"
        }
    }

    # ==================================================
    # 1. Start graph without location and time
    # ==================================================

    result = await app_graph.ainvoke(
        {
            "prompt": "Plan my fishing trip tomorrow."
        },
        config=config,
    )

    print("\n========== STEP 1 ==========")
    print("Result:", result)

    # Graph should pause at location_node
    assert "__interrupt__" in result

    interrupt_data = result["__interrupt__"][0].value

    print("Location Interrupt:", interrupt_data)

    assert interrupt_data["action"] == "GET_LOCATION"


    # ==================================================
    # 2. Resume with location
    # ==================================================

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

    print("\n========== STEP 2 ==========")
    print("Result:", result)

    # Graph should now reach time_node
    assert "__interrupt__" in result

    interrupt_data = result["__interrupt__"][0].value

    print("Time Interrupt:", interrupt_data)

    assert interrupt_data["action"] == "GET_TIME"


    # ==================================================
    # 3. Resume with specific time
    # ==================================================

    result = await app_graph.ainvoke(
        Command(
            resume={
                "slots": [
                    {
                        "date": "2026-09-03",
                        "start_time": "17:00",
                    }
                ],
                "timezone": "Asia/Kolkata",
            }
        ),
        config=config,
    )

    print("\n========== STEP 3 ==========")
    print("Result:", result)

    print("Location:", result.get("location"))
    print("Time Context:", result.get("time_context"))
    print("Selected PFZ:", result.get("selected_pfz"))
    print("PFZ Candidates:", result.get("pfz_candidates"))
    print("Status:", result.get("workflow_status"))

    # ==================================================
    # 4. Verify time was successfully stored
    # ==================================================

    assert result.get("time_context") is not None

    assert len(result["time_context"].slots) == 1

    assert (
        result["time_context"].slots[0].start_time
        == "17:00"
    )

    assert (
        result["time_context"].timezone
        == "Asia/Kolkata"
    )