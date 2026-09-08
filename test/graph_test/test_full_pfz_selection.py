import pytest

from langgraph.types import Command

from ai.graph.graph import app_graph
from ai.schemas.location import Location


@pytest.mark.asyncio
async def test_full_pfz_selection_flow():

    thread_id = "test-full-pfz-selection"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # =====================================================
    # STEP 1
    # Start workflow
    # =====================================================

    result = await app_graph.ainvoke(
        {
            "prompt": "Plan my fishing trip tomorrow.",
            "location": None,
            "time_context": None,
            "distance_km": None,
            "selected_pfz_name": None,
            "route_required": False,
        },
        config=config,
    )

    print("\n" + "=" * 60)
    print("STEP 1 - LOCATION INTERRUPT")
    print("=" * 60)
    print(result)

    assert "__interrupt__" in result

    interrupt_data = result["__interrupt__"][0].value

    assert interrupt_data["action"] == "GET_LOCATION"


    # =====================================================
    # STEP 2
    # Resume with location
    # =====================================================

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

    print("\n" + "=" * 60)
    print("STEP 2 - TIME INTERRUPT")
    print("=" * 60)
    print(result)

    assert "__interrupt__" in result

    interrupt_data = result["__interrupt__"][0].value

    assert interrupt_data["action"] == "GET_TIME"


    # =====================================================
    # STEP 3
    # Resume with time
    # =====================================================

    result = await app_graph.ainvoke(
        Command(
            resume="tomorrow at 5 PM"
        ),
        config=config,
    )

    print("\n" + "=" * 60)
    print("STEP 3 - PFZ SELECTION / RESULT")
    print("=" * 60)
    print(result)

    # -----------------------------------------------------
    # If PFZ candidates exist, we should get SELECT_PFZ
    # -----------------------------------------------------

    if "__interrupt__" in result:

        interrupt_data = result["__interrupt__"][0].value

        print("\nPFZ SELECTION INTERRUPT:")
        print(interrupt_data)

        assert interrupt_data["action"] == "SELECT_PFZ"

        options = interrupt_data["options"]

        assert options
        assert isinstance(options, list)


        # =================================================
        # STEP 4
        # Select first PFZ by NAME
        # =================================================

        selected_pfz_name = options[0]

        print("\nSELECTED PFZ:")
        print(selected_pfz_name)

        result = await app_graph.ainvoke(
            Command(
                resume=selected_pfz_name
            ),
            config=config,
        )

        print("\n" + "=" * 60)
        print("STEP 4 - FINAL RESULT")
        print("=" * 60)
        print(result)

        # Workflow should finish
        assert "__interrupt__" not in result

        assert result.get("selected_pfz_name") == selected_pfz_name

        assert result.get("selected_pfz") is not None

    else:

        # -------------------------------------------------
        # No current PFZ advisory
        # -------------------------------------------------

        print("\nNo PFZ candidates available.")

        assert result.get("workflow_status") == "COMPLETED"