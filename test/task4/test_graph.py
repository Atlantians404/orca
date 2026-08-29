import pytest
from ai.engines.route_engine.pathfinding import astar
from ai.engines.route_engine.graph import create_grid
from ai.engines.route_engine.graph import connect_grid
from ai.engines.route_engine.geometry import create_polygon

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
from ai.engines.route_engine.graph import (
    create_grid,
    connect_grid,
    apply_zone_constraints,
)

def test_restricted_zone_blocks_edge():

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

    restricted_zone = create_polygon(
        [
            (12.99, 80.32),
            (12.99, 80.38),
            (13.01, 80.38),
            (13.01, 80.32),
            (12.99, 80.32)
        ]
    )

    apply_zone_constraints(
        graph,
        restricted_zone
    )

    neighbors = graph.get_neighbors("N8")

    neighbor_ids = {
        edge.target
        for edge in neighbors
    }

    assert "N9" not in neighbor_ids

from ai.engines.route_engine.graph import (
    create_grid,
    connect_grid,
    apply_zone_constraints,
)

from ai.engines.route_engine.geometry import create_polygon

def test_astar_avoids_restricted_zone():

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

    restricted_zone = create_polygon(
        [
            (12.94, 80.29),
            (12.96, 80.37),
            (12.99, 80.37),
            (12.99, 80.29),
            (12.94, 80.29)
        ]
    )

    apply_zone_constraints(
        graph,
        restricted_zone
    )

    path, distance = astar(
        graph,
        "N1",
        "N9"
    )

    assert path[0] == "N1"
    assert path[-1] == "N9"
    assert distance > 0
from ai.engines.route_engine.geometry import (
    create_linestring,
    create_polygon,
    validate_route,
)
def test_validate_safe_route():

    route = create_linestring(
        [
            (12.80, 80.10),
            (12.85, 80.15),
            (12.90, 80.20)
        ]
    )

    restricted_zone = create_polygon(
        [
            (12.95, 80.30),
            (12.95, 80.40),
            (13.05, 80.40),
            (13.05, 80.30),
            (12.95, 80.30)
        ]
    )

    assert validate_route(
        route,
        [restricted_zone]
    ) is True

def test_validate_unsafe_route():

    route = create_linestring(
        [
            (12.90, 80.20),
            (13.00, 80.35),
            (13.10, 80.50)
        ]
    )

    restricted_zone = create_polygon(
        [
            (12.95, 80.30),
            (12.95, 80.40),
            (13.05, 80.40),
            (13.05, 80.30),
            (12.95, 80.30)
        ]
    )

    assert validate_route(
        route,
        [restricted_zone]
    ) is False

def test_validate_route_multiple_zones():

    route = create_linestring(
        [
            (12.80, 80.10),
            (12.85, 80.15),
            (12.90, 80.20)
        ]
    )

    zone_1 = create_polygon(
        [
            (12.95, 80.30),
            (12.95, 80.40),
            (13.05, 80.40),
            (13.05, 80.30),
            (12.95, 80.30)
        ]
    )

    zone_2 = create_polygon(
        [
            (12.70, 80.05),
            (12.70, 80.15),
            (12.75, 80.15),
            (12.75, 80.05),
            (12.70, 80.05)
        ]
    )

    assert validate_route(
        route,
        [zone_1, zone_2]
    ) is True

from ai.engines.route_engine.graph import (
    path_to_coordinates,
)
def test_path_to_coordinates():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05
    )

    path = [
        "N1",
        "N2",
        "N5",
        "N8",
        "N9"
    ]

    coordinates = path_to_coordinates(
        graph,
        path
    )

    assert coordinates == [
        (12.90, 80.30),
        (12.90, 80.35),
        (12.95, 80.35),
        (13.00, 80.35),
        (13.00, 80.40)
    ]
def test_path_to_coordinates_invalid_node():

    graph = create_grid(
        start_latitude=12.90,
        start_longitude=80.30,
        rows=3,
        columns=3,
        latitude_step=0.05,
        longitude_step=0.05
    )

    with pytest.raises(ValueError):

        path_to_coordinates(
            graph,
            ["N1", "N99"]
        )
