import pytest

from ai.engines.route_engine.graph import (
    create_grid,
    connect_grid,
)

from ai.engines.route_engine.pathfinding import dijkstra

def test_dijkstra_finds_path():

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

    path, distance = dijkstra(
        graph,
        "N1",
        "N9"
    )

    assert path[0] == "N1"
    assert path[-1] == "N9"

    assert distance > 0

def test_dijkstra_path_is_connected():

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

    path, _ = dijkstra(
        graph,
        "N1",
        "N9"
    )

    for source, target in zip(
        path,
        path[1:]
    ):

        neighbors = graph.get_neighbors(source)

        neighbor_ids = {
            edge.target
            for edge in neighbors
        }

        assert target in neighbor_ids
from ai.engines.route_engine.graph import (
    Node,
    MarineGraph,
)

from ai.engines.route_engine.pathfinding import dijkstra

def test_dijkstra_no_path():

    graph = MarineGraph()

    graph.add_node(
        Node(
            id="N1",
            latitude=12.90,
            longitude=80.30
        )
    )

    graph.add_node(
        Node(
            id="N2",
            latitude=13.00,
            longitude=80.40
        )
    )

    with pytest.raises(ValueError):

        dijkstra(
            graph,
            "N1",
            "N2"
        )
from ai.engines.route_engine.pathfinding import astar
def test_astar_finds_path():

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

    path, distance = astar(
        graph,
        "N1",
        "N9"
    )

    assert path[0] == "N1"
    assert path[-1] == "N9"

    assert distance > 0
def test_astar_matches_dijkstra():

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

    dijkstra_path, dijkstra_distance = dijkstra(
        graph,
        "N1",
        "N9"
    )

    astar_path, astar_distance = astar(
        graph,
        "N1",
        "N9"
    )

    assert astar_path[0] == "N1"
    assert astar_path[-1] == "N9"

    assert astar_distance == pytest.approx(
        dijkstra_distance,
        abs=0.001
    )
from ai.engines.route_engine.graph import (
    Node,
    MarineGraph,
)

def test_astar_no_path():

    graph = MarineGraph()

    graph.add_node(
        Node(
            id="N1",
            latitude=12.90,
            longitude=80.30
        )
    )

    graph.add_node(
        Node(
            id="N2",
            latitude=13.00,
            longitude=80.40
        )
    )

    with pytest.raises(ValueError):

        astar(
            graph,
            "N1",
            "N2"
        )