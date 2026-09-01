import pytest

from ai.engines.route_engine.graph import (
    create_grid,
    connect_grid,
)

from ai.engines.route_engine.pathfinding import (
    dijkstra,
    astar,
    calculate_path_distance,
    generate_candidate_paths,
)


def create_test_graph():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    connect_grid(
        graph,
        rows=3,
        columns=3,
    )

    return graph


# =========================================================
# DIJKSTRA
# =========================================================

def test_dijkstra():

    graph = create_test_graph()

    path, distance = dijkstra(
        graph,
        "N1",
        "N9",
    )

    assert path[0] == "N1"

    assert path[-1] == "N9"

    assert distance > 0


def test_dijkstra_invalid_start():

    graph = create_test_graph()

    with pytest.raises(ValueError):

        dijkstra(
            graph,
            "INVALID",
            "N9",
        )


def test_dijkstra_invalid_goal():

    graph = create_test_graph()

    with pytest.raises(ValueError):

        dijkstra(
            graph,
            "N1",
            "INVALID",
        )


# =========================================================
# A*
# =========================================================

def test_astar():

    graph = create_test_graph()

    path, distance = astar(
        graph,
        "N1",
        "N9",
    )

    assert path[0] == "N1"

    assert path[-1] == "N9"

    assert distance > 0


def test_astar_invalid_start():

    graph = create_test_graph()

    with pytest.raises(ValueError):

        astar(
            graph,
            "INVALID",
            "N9",
        )


def test_astar_invalid_goal():

    graph = create_test_graph()

    with pytest.raises(ValueError):

        astar(
            graph,
            "N1",
            "INVALID",
        )


def test_astar_distance_positive():

    graph = create_test_graph()

    path, distance = astar(
        graph,
        "N1",
        "N9",
    )

    assert len(path) >= 2

    assert distance > 0


# =========================================================
# PATH DISTANCE
# =========================================================

def test_calculate_path_distance():

    graph = create_test_graph()

    path = [
        "N1",
        "N5",
        "N9",
    ]

    distance = calculate_path_distance(
        graph,
        path,
    )

    assert distance > 0


def test_calculate_empty_path_distance():

    graph = create_test_graph()

    distance = calculate_path_distance(
        graph,
        [],
    )

    assert distance == 0


def test_calculate_single_node_distance():

    graph = create_test_graph()

    distance = calculate_path_distance(
        graph,
        ["N1"],
    )

    assert distance == 0


def test_calculate_invalid_edge_distance():

    graph = create_test_graph()

    with pytest.raises(ValueError):

        calculate_path_distance(
            graph,
            [
                "N1",
                "N9",
            ],
        )


# =========================================================
# CANDIDATE ROUTES
# =========================================================

def test_generate_candidate_paths():

    graph = create_test_graph()

    candidates = generate_candidate_paths(
        graph,
        "N1",
        "N9",
        max_routes=3,
    )

    assert len(candidates) >= 1

    assert len(candidates) <= 3


def test_candidate_paths_start_and_end_correctly():

    graph = create_test_graph()

    candidates = generate_candidate_paths(
        graph,
        "N1",
        "N9",
        max_routes=3,
    )

    for path, distance in candidates:

        assert path[0] == "N1"

        assert path[-1] == "N9"

        assert distance > 0


def test_candidate_paths_are_unique():

    graph = create_test_graph()

    candidates = generate_candidate_paths(
        graph,
        "N1",
        "N9",
        max_routes=3,
    )

    paths = [
        tuple(path)
        for path, _ in candidates
    ]

    assert len(paths) == len(
        set(paths)
    )


def test_candidate_paths_have_valid_distances():

    graph = create_test_graph()

    candidates = generate_candidate_paths(
        graph,
        "N1",
        "N9",
        max_routes=3,
    )

    for path, distance in candidates:

        calculated_distance = (
            calculate_path_distance(
                graph,
                path,
            )
        )

        assert distance == pytest.approx(
            calculated_distance
        )


def test_candidate_paths_invalid_start():

    graph = create_test_graph()

    with pytest.raises(ValueError):

        generate_candidate_paths(
            graph,
            "INVALID",
            "N9",
            max_routes=3,
        )


def test_candidate_paths_invalid_goal():

    graph = create_test_graph()

    with pytest.raises(ValueError):

        generate_candidate_paths(
            graph,
            "N1",
            "INVALID",
            max_routes=3,
        )


def test_candidate_paths_invalid_max_routes():

    graph = create_test_graph()

    with pytest.raises(ValueError):

        generate_candidate_paths(
            graph,
            "N1",
            "N9",
            max_routes=0,
        )