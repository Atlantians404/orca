import pytest

from ai.engines.route_engine.engine import RouteEngine
from ai.engines.route_engine.schemas import (
    Coordinate,
    RouteDestination,
    RouteRequest,
)


# =========================================================
# TEST DATA
# =========================================================

START = Coordinate(
    latitude=13.0500,
    longitude=80.2500,
)

DESTINATION = RouteDestination(
    coastal_reference="KATHIVAKKAM_01",
    latitude=13.494444,
    longitude=80.379444,
)


TIME = "2026-09-05T08:00:00"


def create_request():

    return RouteRequest(
        start=START,
        destination=DESTINATION,
    )


# =========================================================
# MAX ROUTES = 0
# =========================================================

def test_invalid_max_routes_zero():

    engine = RouteEngine()

    request = create_request()

    with pytest.raises(ValueError):

        engine.generate_routes(
            request=request,
            time=TIME,
            max_routes=0,
            rows=10,
            columns=10,
        )


# =========================================================
# MAX ROUTES < 0
# =========================================================

def test_invalid_max_routes_negative():

    engine = RouteEngine()

    request = create_request()

    with pytest.raises(ValueError):

        engine.generate_routes(
            request=request,
            time=TIME,
            max_routes=-1,
            rows=10,
            columns=10,
        )


# =========================================================
# MAX ROUTES = 1
# =========================================================

def test_max_routes_one():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TIME,
        max_routes=1,
        rows=10,
        columns=10,
    )

    assert result is not None

    assert result.routes is not None

    assert len(result.routes) <= 1


# =========================================================
# MAX ROUTES LIMIT
# =========================================================

def test_max_routes_limit():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TIME,
        max_routes=2,
        rows=10,
        columns=10,
    )

    assert result is not None

    assert len(result.routes) <= 2


# =========================================================
# VALID REQUEST
# =========================================================

def test_valid_request_does_not_raise():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TIME,
        max_routes=1,
        rows=10,
        columns=10,
    )

    assert result is not None


# =========================================================
# START AND DESTINATION ARE DIFFERENT
# =========================================================

def test_start_and_destination_are_different():

    request = create_request()

    assert (
        request.start.latitude
        != request.destination.latitude
        or
        request.start.longitude
        != request.destination.longitude
    )


# =========================================================
# INVALID LATITUDE
# =========================================================

def test_invalid_start_latitude():

    with pytest.raises(Exception):

        Coordinate(
            latitude=100.0,
            longitude=80.2500,
        )


# =========================================================
# INVALID LONGITUDE
# =========================================================

def test_invalid_start_longitude():

    with pytest.raises(Exception):

        Coordinate(
            latitude=13.0500,
            longitude=200.0,
        )


# =========================================================
# INVALID DESTINATION LATITUDE
# =========================================================

def test_invalid_destination_latitude():

    with pytest.raises(Exception):

        RouteDestination(
            coastal_reference="INVALID",
            latitude=100.0,
            longitude=80.379444,
        )


# =========================================================
# INVALID DESTINATION LONGITUDE
# =========================================================

def test_invalid_destination_longitude():

    with pytest.raises(Exception):

        RouteDestination(
            coastal_reference="INVALID",
            latitude=13.494444,
            longitude=200.0,
        )


# =========================================================
# REQUEST CONTAINS START
# =========================================================

def test_request_contains_start():

    request = create_request()

    assert request.start is not None

    assert (
        request.start.latitude
        == 13.0500
    )

    assert (
        request.start.longitude
        == 80.2500
    )


# =========================================================
# REQUEST CONTAINS DESTINATION
# =========================================================

def test_request_contains_destination():

    request = create_request()

    assert request.destination is not None

    assert (
        request.destination.latitude
        == 13.494444
    )

    assert (
        request.destination.longitude
        == 80.379444
    )


# =========================================================
# ROUTE RESULT HAS ROUTES
# =========================================================

def test_result_contains_routes():

    engine = RouteEngine()

    request = create_request()

    result = engine.generate_routes(
        request=request,
        time=TIME,
        max_routes=1,
        rows=10,
        columns=10,
    )

    assert hasattr(
        result,
        "routes",
    )

    assert result.routes is not None