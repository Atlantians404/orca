import pytest

from ai.graph.nodes import location_node
from ai.schemas.location import Location


@pytest.mark.asyncio
async def test_location_with_coordinates():

    state = {
        "location": Location(
            latitude=13.0827,
            longitude=80.2707
        )
    }

    result = await location_node(state)

    assert result["location"].latitude == 13.0827
    assert result["location"].longitude == 80.2707
    assert result["workflow_status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_location_missing():

    state = {}

    result = await location_node(state)

    assert result["pending_action"] == "GET_LOCATION"
    assert result["workflow_status"] == "WAITING_FOR_USER"