import pytest

from ai.graph.nodes import pfz_node
from ai.schemas.location import Location


@pytest.mark.asyncio
async def test_direct_pfz_resolution():
    """
    User directly specifies a PFZ/coastal reference.
    It should be converted to coordinates and stored
    in selected_pfz.
    """

    state = {
        "selected_pfz_name": "Pondicherry"
    }

    result = await pfz_node(state)

    assert result["selected_pfz"] is not None

    assert result["selected_pfz"]["pfz_name"] == "Pondicherry"

    assert result["selected_pfz"]["latitude"] == 11.873056
    assert result["selected_pfz"]["longitude"] == 80.064722

    assert result["workflow_status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_pfz_without_selection_and_generate_candidates():
    """
    No direct PFZ is provided.
    PFZ candidates should be generated using the
    user's location and default radius.
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

    assert "pfz_candidates" in result
    assert result["pfz_candidates"] is not None

    assert result["workflow_status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_pfz_with_custom_distance():
    """
    User explicitly provides a search distance.
    That distance should be passed to the PFZ candidate function.
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

    assert "pfz_candidates" in result
    assert result["pfz_candidates"] is not None

    assert result["workflow_status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_pfz_missing_location():
    """
    Candidate generation cannot happen without a location.
    """

    state = {
        "distance_km": 20,
    }

    result = await pfz_node(state)

    assert result["pending_action"] == "GET_LOCATION"
    assert result["workflow_status"] == "WAITING_FOR_USER"