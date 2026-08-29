from ai.engines.route_engine.schemas import (
    RouteRequest,
)


def test_route_request():

    request = RouteRequest(
        start={
            "latitude": 13.05,
            "longitude": 80.28
        },
        destination={
            "pfz_id": "PFZ07",
            "latitude": 13.12,
            "longitude": 80.42
        },
        time="07:00"
    )

    assert request.start.latitude == 13.05
    assert request.start.longitude == 80.28

    assert request.destination.pfz_id == "PFZ07"

    assert request.time == "07:00"

    assert (
        request.constraints.avoid_restricted_zones
        is True
    )