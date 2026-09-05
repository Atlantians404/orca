import pytest

from ai.engines.route_engine.graph import (
    MarineGraph,
    Node,
)

from ai.engines.route_engine.schemas import Waypoint

from ai.engines.route_engine.waypoints import (
    generate_waypoints,
    generate_waypoints_from_coordinates,
    validate_waypoints,
)


# =========================================================
# GRAPH WAYPOINTS
# =========================================================

def test_generate_waypoints():

    graph = MarineGraph()

    graph.add_node(
        Node(
            id="N1",
            latitude=13.08,
            longitude=80.27,
        )
    )

    graph.add_node(
        Node(
            id="N2",
            latitude=13.09,
            longitude=80.28,
        )
    )

    graph.add_node(
        Node(
            id="N3",
            latitude=13.10,
            longitude=80.29,
        )
    )

    path = [
        "N1",
        "N2",
        "N3",
    ]

    waypoints = generate_waypoints(
        graph,
        path,
    )

    assert len(waypoints) == 1

    assert waypoints[0].latitude == 13.09
    assert waypoints[0].longitude == 80.28


# =========================================================
# START + DESTINATION ONLY
# =========================================================

def test_no_intermediate_waypoints():

    graph = MarineGraph()

    graph.add_node(
        Node(
            id="START",
            latitude=13.08,
            longitude=80.27,
        )
    )

    graph.add_node(
        Node(
            id="DEST",
            latitude=13.10,
            longitude=80.29,
        )
    )

    waypoints = generate_waypoints(
        graph,
        [
            "START",
            "DEST",
        ],
    )

    assert waypoints == []


# =========================================================
# COORDINATE WAYPOINTS
# =========================================================

def test_generate_waypoints_from_coordinates():

    coordinates = [
        (13.08, 80.27),
        (13.09, 80.28),
        (13.10, 80.29),
    ]

    waypoints = generate_waypoints_from_coordinates(
        coordinates
    )

    assert len(waypoints) == 1

    assert waypoints[0].latitude == 13.09
    assert waypoints[0].longitude == 80.28


# =========================================================
# EMPTY COORDINATES
# =========================================================

def test_empty_coordinates():

    with pytest.raises(ValueError):

        generate_waypoints_from_coordinates(
            []
        )


# =========================================================
# EMPTY PATH
# =========================================================

def test_empty_path():

    graph = MarineGraph()

    with pytest.raises(ValueError):

        generate_waypoints(
            graph,
            [],
        )


# =========================================================
# UNKNOWN NODE
# =========================================================

def test_unknown_node():

    graph = MarineGraph()

    graph.add_node(
        Node(
            id="N1",
            latitude=13.08,
            longitude=80.27,
        )
    )

    with pytest.raises(ValueError):

        generate_waypoints(
            graph,
            [
                "N1",
                "UNKNOWN",
                "N2",
            ],
        )


# =========================================================
# VALID WAYPOINTS
# =========================================================

def test_validate_waypoints():

    waypoints = [
        Waypoint(
            latitude=13.09,
            longitude=80.28,
        )
    ]

    assert validate_waypoints(
        waypoints
    ) is True


# =========================================================
# INVALID LATITUDE
# =========================================================

def test_invalid_latitude():

    waypoint = Waypoint(
        latitude=100.0,
        longitude=80.27,
    )

    assert validate_waypoints(
        [waypoint]
    ) is False


# =========================================================
# INVALID LONGITUDE
# =========================================================

def test_invalid_longitude():

    waypoint = Waypoint(
        latitude=13.08,
        longitude=200.0,
    )

    assert validate_waypoints(
        [waypoint]
    ) is False


# =========================================================
# MULTIPLE INTERMEDIATE WAYPOINTS
# =========================================================

def test_multiple_waypoints():

    coordinates = [
        (13.08, 80.27),
        (13.09, 80.28),
        (13.10, 80.29),
        (13.11, 80.30),
        (13.12, 80.31),
    ]

    waypoints = generate_waypoints_from_coordinates(
        coordinates
    )

    assert len(waypoints) == 3

    assert waypoints[0].latitude == 13.09
    assert waypoints[1].latitude == 13.10
    assert waypoints[2].latitude == 13.11


# =========================================================
# ONE COORDINATE
# =========================================================

def test_single_coordinate():

    coordinates = [
        (13.08, 80.27),
    ]

    waypoints = generate_waypoints_from_coordinates(
        coordinates
    )

    assert waypoints == []


# =========================================================
# TWO COORDINATES
# =========================================================

def test_two_coordinates():

    coordinates = [
        (13.08, 80.27),
        (13.10, 80.29),
    ]

    waypoints = generate_waypoints_from_coordinates(
        coordinates
    )

    assert waypoints == []