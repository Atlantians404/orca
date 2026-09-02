import pytest

from ai.graph.nodes import pfz_node


@pytest.mark.asyncio
async def test_direct_pfz_resolution():

    state = {
        "selected_pfz_id": "Pondicherry"
    }

    result = await pfz_node(state)

    assert result["selected_pfz"]["pfz_name"] == "Pondicherry"
    assert "latitude" in result["selected_pfz"]
    assert "longitude" in result["selected_pfz"]
    assert result["workflow_status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_pfz_without_selection():

    state = {
        "location": {
            "latitude": 13.0827,
            "longitude": 80.2707
        }
    }

    result = await pfz_node(state)

    assert result["pending_action"] == "GENERATE_PFZ_CANDIDATES"
    assert result["workflow_status"] == "IN_PROGRESS"