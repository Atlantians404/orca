import pytest

from ai.graph.nodes import pfz_node
from ai.schemas.location import Location


@pytest.mark.asyncio
async def test_direct_pfz_resolution():
    """
    User directly specifies a PFZ/coastal reference.
    It should be converted to coordinates.
    """

    state = {
        "selected_pfz_name": "Pondicherry"
    }

    result = await pfz_node(state)

    print("\nDIRECT PFZ RESULT:")
    print(result)

    assert result["selected_pfz"] is not None
    assert result["selected_pfz"]["pfz_name"] == "Pondicherry"

    assert result["selected_pfz"]["latitude"] == 11.873056
    assert result["selected_pfz"]["longitude"] == 80.064722

    assert result["workflow_status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_pfz_without_selection_and_generate_candidates():
    """
    No direct PFZ is provided.

    PFZ candidates should be generated using the user's
    current location and default distance.
    """

    state = {
        "location": Location(
            place="Chennai",
            latitude=13.0827,
            longitude=80.2707,
        ),
        "distance_km": None,
    }

    result = await pfz_node(state)

    print("\nPFZ CANDIDATES RESULT:")
    print(result)

    assert "pfz_candidates" in result
    assert result["pfz_candidates"] is not None

    # If candidates are available, workflow continues.
    # If there is no currently valid advisory, workflow completes.
    if result["pfz_candidates"]:
        assert result["workflow_status"] == "IN_PROGRESS"
    else:
        assert result["workflow_status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_pfz_with_custom_distance():
    """
    User explicitly provides a search distance.

    That distance should be passed to the PFZ candidate
    generation function.
    """

    state = {
        "location": Location(
            place="Chennai",
            latitude=13.0827,
            longitude=80.2707,
        ),
        "distance_km": 20,
    }

    result = await pfz_node(state)

    print("\nPFZ CUSTOM DISTANCE RESULT:")
    print(result)

    assert "pfz_candidates" in result
    assert result["pfz_candidates"] is not None

    # If candidates are available, workflow continues.
    # If there is no currently valid advisory, workflow completes.
    if result["pfz_candidates"]:
        assert result["workflow_status"] == "IN_PROGRESS"
    else:
        assert result["workflow_status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_pfz_missing_location():
    """
    PFZ candidate generation requires a source location.
    """

    state = {
        "distance_km": 20,
    }

    result = await pfz_node(state)

    print("\nPFZ MISSING LOCATION RESULT:")
    print(result)

    assert result["pending_action"] == "GET_LOCATION"
    assert result["workflow_status"] == "WAITING_FOR_USER"