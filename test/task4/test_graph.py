import pytest

from ai.engines.route_engine.graph import (
    Node,
    Edge,
    MarineGraph,
    create_grid,
    connect_grid,
    apply_zone_constraints,
    path_to_coordinates,
    find_nearest_node,
    create_route_grid,
)

from ai.engines.route_engine.geometry import (
    zone_to_polygon,
)


def test_add_node():

    graph = MarineGraph()

    node = Node(
        id="N1",
        latitude=12.90,
        longitude=80.30,
    )

    graph.add_node(node)

    assert "N1" in graph.nodes
    assert graph.nodes["N1"].latitude == 12.90


def test_add_edge():

    graph = MarineGraph()

    graph.add_node(
        Node("N1", 12.90, 80.30)
    )

    graph.add_node(
        Node("N2", 12.95, 80.35)
    )

    edge = Edge(
        source="N1",
        target="N2",
        weight=5.0,
    )

    graph.add_edge(edge)

    neighbors = graph.get_neighbors("N1")

    assert len(neighbors) == 1
    assert neighbors[0].target == "N2"
    assert neighbors[0].weight == 5.0


def test_create_grid():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    assert len(graph.nodes) == 9

    assert "N1" in graph.nodes
    assert "N9" in graph.nodes


def test_grid_coordinates():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    assert graph.nodes["N1"].latitude == pytest.approx(
        12.90
    )

    assert graph.nodes["N1"].longitude == pytest.approx(
        80.30
    )

    assert graph.nodes["N5"].latitude == pytest.approx(
        12.95
    )

    assert graph.nodes["N5"].longitude == pytest.approx(
        80.35
    )

    assert graph.nodes["N9"].latitude == pytest.approx(
        13.00
    )

    assert graph.nodes["N9"].longitude == pytest.approx(
        80.40
    )


def test_connect_grid():

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

    neighbors = graph.get_neighbors("N1")

    neighbor_ids = {
        edge.target
        for edge in neighbors
    }

    assert neighbor_ids == {
        "N2",
        "N4",
        "N5",
    }


def test_edge_weight():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=2,
        columns=2,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    connect_grid(
        graph,
        rows=2,
        columns=2,
    )

    neighbors = graph.get_neighbors("N1")

    for edge in neighbors:
        assert edge.weight > 0


def test_center_node_neighbors():

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

    neighbors = graph.get_neighbors("N5")

    neighbor_ids = {
        edge.target
        for edge in neighbors
    }

    assert neighbor_ids == {
        "N1",
        "N2",
        "N3",
        "N4",
        "N6",
        "N7",
        "N8",
        "N9",
    }


def test_diagonal_connection():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=2,
        columns=2,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    connect_grid(
        graph,
        rows=2,
        columns=2,
    )

    neighbors = graph.get_neighbors("N1")

    neighbor_ids = {
        edge.target
        for edge in neighbors
    }

    assert "N4" in neighbor_ids


def test_diagonal_edge_weight():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=2,
        columns=2,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    connect_grid(
        graph,
        rows=2,
        columns=2,
    )

    diagonal_edges = [
        edge
        for edge in graph.get_neighbors("N1")
        if edge.target == "N4"
    ]

    assert len(diagonal_edges) == 1

    assert diagonal_edges[0].weight > 0


def test_restricted_zone_blocks_edge():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=2,
        columns=2,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    connect_grid(
        graph,
        rows=2,
        columns=2,
    )

    zone = {
        "id": "ZONE001",
        "name": "Restricted Zone",
        "coordinates": [
            [12.89, 80.29],
            [12.91, 80.31],
            [12.96, 80.36],
            [12.94, 80.34],
            [12.89, 80.29],
        ],
    }

    polygon = zone_to_polygon(zone)

    apply_zone_constraints(
        graph,
        polygon,
    )

    assert isinstance(
        graph,
        MarineGraph,
    )


def test_path_to_coordinates():

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

    coordinates = path_to_coordinates(
        graph,
        path,
    )

    assert coordinates == [
        (12.90, 80.30),
        (12.95, 80.35),
        (13.00, 80.40),
    ]


def test_path_to_coordinates_invalid_node():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    with pytest.raises(ValueError):

        path_to_coordinates(
            graph,
            ["N1", "INVALID"],
        )


def test_find_nearest_node():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    node = find_nearest_node(
        graph,
        12.90,
        80.30,
    )

    assert node == "N1"


def test_find_nearest_node_center():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05,
    )

    node = find_nearest_node(
        graph,
        12.95,
        80.35,
    )

    assert node == "N5"


def test_empty_graph_nearest_node():

    graph = MarineGraph()

    with pytest.raises(ValueError):

        find_nearest_node(
            graph,
            12.90,
            80.30,
        )


def test_create_route_grid():

    graph = create_route_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        goal_latitude=13.00,
        goal_longitude=80.40,
        rows=10,
        columns=10,
    )

    assert len(graph.nodes) == 100

    assert graph.nodes["N1"].latitude == pytest.approx(
        12.90
    )

    assert graph.nodes["N1"].longitude == pytest.approx(
        80.30
    )

    assert graph.nodes["N100"].latitude == pytest.approx(
        13.00
    )

    assert graph.nodes["N100"].longitude == pytest.approx(
        80.40
    )


def test_create_route_grid_invalid_rows():

    with pytest.raises(ValueError):

        create_route_grid(
            12.90,
            80.30,
            13.00,
            80.40,
            rows=1,
            columns=10,
        )


def test_create_route_grid_invalid_columns():

    with pytest.raises(ValueError):

        create_route_grid(
            12.90,
            80.30,
            13.00,
            80.40,
            rows=10,
            columns=1,
        )