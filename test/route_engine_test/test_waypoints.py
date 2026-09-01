import pytest

from ai.engines.route_engine.graph import (
    create_grid,
)

from ai.engines.route_engine.waypoints import (
    generate_waypoints,
    generate_waypoints_from_coordinates,
    validate_waypoints,
)

from ai.engines.route_engine.schemas import Waypoint


# =========================================================
# generate_waypoints()
# =========================================================

def test_generate_waypoints():
    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    path = [
        "N1",
        "N2",
        "N5",
        "N8",
        "N9",
    ]

    waypoints = generate_waypoints(
        graph,
        path
    )

    assert len(waypoints) == 3

    assert waypoints[0].latitude == pytest.approx(12.90)
    assert waypoints[0].longitude == pytest.approx(80.35)

    assert waypoints[1].latitude == pytest.approx(12.95)
    assert waypoints[1].longitude == pytest.approx(80.35)

    assert waypoints[2].latitude == pytest.approx(13.00)
    assert waypoints[2].longitude == pytest.approx(80.35)


def test_generate_waypoints_excludes_start_and_destination():
    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    path = [
        "N1",
        "N5",
        "N9",
    ]

    waypoints = generate_waypoints(
        graph,
        path
    )

    assert len(waypoints) == 1

    assert waypoints[0].latitude == pytest.approx(12.95)
    assert waypoints[0].longitude == pytest.approx(80.35)


def test_generate_waypoints_two_node_path():
    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=2,
        columns=2,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    path = [
        "N1",
        "N4",
    ]

    waypoints = generate_waypoints(
        graph,
        path
    )

    assert waypoints == []


def test_generate_waypoints_empty_path():

    with pytest.raises(ValueError):

        generate_waypoints(
            create_grid(
                start_latitude=12.90,
                start_longitude=80.30,
                rows=2,
                columns=2,
                latitude_step=0.05,
                longitude_step=0.05,
            ),
            []
        )


def test_generate_waypoints_invalid_node():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    path = [
        "N1",
        "N5",
        "INVALID",
        "N9",
    ]

    with pytest.raises(ValueError):

        generate_waypoints(
            graph,
            path
        )


# =========================================================
# generate_waypoints_from_coordinates()
# =========================================================

def test_generate_waypoints_from_coordinates():

    coordinates = [
        (12.90, 80.30),
        (12.95, 80.35),
        (13.00, 80.40),
    ]

    waypoints = generate_waypoints_from_coordinates(
        coordinates
    )

    assert len(waypoints) == 1

    assert waypoints[0].latitude == pytest.approx(12.95)
    assert waypoints[0].longitude == pytest.approx(80.35)


def test_generate_multiple_waypoints_from_coordinates():

    coordinates = [
        (12.90, 80.30),
        (12.92, 80.32),
        (12.95, 80.35),
        (12.98, 80.38),
        (13.00, 80.40),
    ]

    waypoints = generate_waypoints_from_coordinates(
        coordinates
    )

    assert len(waypoints) == 3

    assert waypoints[0].latitude == pytest.approx(12.92)
    assert waypoints[1].latitude == pytest.approx(12.95)
    assert waypoints[2].latitude == pytest.approx(12.98)


def test_generate_waypoints_from_coordinates_empty():

    with pytest.raises(ValueError):

        generate_waypoints_from_coordinates([])


def test_generate_waypoints_from_coordinates_two_points():

    coordinates = [
        (12.90, 80.30),
        (13.00, 80.40),
    ]

    waypoints = generate_waypoints_from_coordinates(
        coordinates
    )

    assert waypoints == []


# =========================================================
# validate_waypoints()
# =========================================================

def test_validate_waypoints():

    waypoints = [
        Waypoint(
            latitude=12.95,
            longitude=80.35
        ),
        Waypoint(
            latitude=13.00,
            longitude=80.40
        ),
    ]

    assert validate_waypoints(
        waypoints
    ) is True


def test_validate_waypoints_empty():

    assert validate_waypoints([]) is True


def test_validate_waypoints_invalid_latitude():

    # Construct manually so we can test the validator itself.
    waypoint = Waypoint(
        latitude=90.0,
        longitude=80.0
    )

    assert validate_waypoints(
        [waypoint]
    ) is True


def test_validate_waypoints_invalid_longitude():

    waypoint = Waypoint(
        latitude=13.0,
        longitude=180.0
    )

    assert validate_waypoints(
        [waypoint]
    ) is True