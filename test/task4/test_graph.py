from ai.engines.route_engine.graph import create_grid
from ai.engines.route_engine.graph import connect_grid

from ai.engines.route_engine.graph import (
    Node,
    Edge,
    MarineGraph,
)


def test_add_node():

    graph = MarineGraph()

    node = Node(
        id="N1",
        latitude=13.00,
        longitude=80.30
    )

    graph.add_node(node)

    assert "N1" in graph.nodes
    assert graph.nodes["N1"].latitude == 13.00

def test_add_edge():

    graph = MarineGraph()

    graph.add_node(
        Node(
            id="N1",
            latitude=13.00,
            longitude=80.30
        )
    )

    graph.add_node(
        Node(
            id="N2",
            latitude=13.00,
            longitude=80.35
        )
    )

    edge = Edge(
        source="N1",
        target="N2",
        weight=5.4
    )

    graph.add_edge(edge)

    neighbors = graph.get_neighbors("N1")

    assert len(neighbors) == 1
    assert neighbors[0].target == "N2"
    assert neighbors[0].weight == 5.4

def test_create_grid():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05
    )

    assert len(graph.nodes) == 9

    assert "N1" in graph.nodes
    assert "N5" in graph.nodes
    assert "N9" in graph.nodes

def test_grid_coordinates():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05
    )

    n1 = graph.nodes["N1"]
    n5 = graph.nodes["N5"]
    n9 = graph.nodes["N9"]

    assert n1.latitude == 12.90
    assert n1.longitude == 80.30

    assert n5.latitude == 12.95
    assert n5.longitude == 80.35

    assert n9.latitude == 13.00
    assert n9.longitude == 80.40

def test_connect_grid():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05
    )

    connect_grid(
        graph,
        rows=3,
        columns=3
    )

    neighbors = graph.get_neighbors("N1")

    assert len(neighbors) == 2

    neighbor_ids = {
        edge.target
        for edge in neighbors
    }

    assert neighbor_ids == {"N2", "N4"}
def test_edge_weight():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05
    )

    connect_grid(
        graph,
        rows=3,
        columns=3
    )

    edges = graph.get_neighbors("N1")

    for edge in edges:
        assert edge.weight > 0
def test_center_node_neighbors():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05
    )

    connect_grid(
        graph,
        rows=3,
        columns=3
    )

    neighbors = graph.get_neighbors("N5")

    neighbor_ids = {
        edge.target
        for edge in neighbors
    }

    assert neighbor_ids == {
        "N2",
        "N4",
        "N6",
        "N8"
    }
