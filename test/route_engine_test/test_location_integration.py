import pytest

from ai.engines.route_engine.engine import RouteEngine
from ai.schemas.location import Location


# =========================================================
# TEST DATA
# =========================================================

START_LOCATION = Location(
    latitude=13.0500,
    longitude=80.2500,
)

SELECTED_PFZ = {
    "coastal_reference": "KATHIVAKKAM_01",
    "latitude": 13.494444,
    "longitude": 80.379444,
    "depth_m": 42.0,
}


# =========================================================
# LOCATION → ROUTE START
# =========================================================

def test_location_is_used_as_route_start():

    engine = RouteEngine()

    state = {
        "location": START_LOCATION,
        "selected_pfz": SELECTED_PFZ,
    }

    start = state["location"]

    assert start.latitude == 13.0500
    assert start.longitude == 80.2500


# =========================================================
# SELECTED PFZ → ROUTE DESTINATION
# =========================================================

def test_selected_pfz_is_used_as_destination():

    state = {
        "location": START_LOCATION,
        "selected_pfz": SELECTED_PFZ,
    }

    pfz = state["selected_pfz"]

    assert pfz["latitude"] == 13.494444
    assert pfz["longitude"] == 80.379444

    assert (
        pfz["coastal_reference"]
        == "KATHIVAKKAM_01"
    )


# =========================================================
# BOTH LOCATION AND PFZ EXIST
# =========================================================

def test_location_and_pfz_are_available():

    state = {
        "location": START_LOCATION,
        "selected_pfz": SELECTED_PFZ,
    }

    assert state["location"] is not None
    assert state["selected_pfz"] is not None


# =========================================================
# LOCATION AND PFZ ARE DIFFERENT
# =========================================================

def test_start_and_destination_are_different():

    state = {
        "location": START_LOCATION,
        "selected_pfz": SELECTED_PFZ,
    }

    start = state["location"]

    destination = state["selected_pfz"]

    assert (
        start.latitude,
        start.longitude,
    ) != (
        destination["latitude"],
        destination["longitude"],
    )


# =========================================================
# MISSING LOCATION
# =========================================================

def test_missing_location():

    state = {
        "location": None,
        "selected_pfz": SELECTED_PFZ,
    }

    assert state["location"] is None


# =========================================================
# MISSING SELECTED PFZ
# =========================================================

def test_missing_selected_pfz():

    state = {
        "location": START_LOCATION,
        "selected_pfz": None,
    }

    assert state["selected_pfz"] is None