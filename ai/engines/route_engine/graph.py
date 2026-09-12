from dataclasses import dataclass

from .geometry import (
    create_linestring,
    route_intersects_polygon,
)


@dataclass
class Node:
    id: str
    latitude: float
    longitude: float


@dataclass
class Edge:
    source: str
    target: str
    weight: float


class MarineGraph:

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, list[Edge]] = {}

    def add_node(
        self,
        node: Node,
    ):
        self.nodes[node.id] = node
        self.edges.setdefault(
            node.id,
            [],
        )

    def add_edge(
        self,
        edge: Edge,
    ):
        if edge.source not in self.nodes:
            raise ValueError(
                f"Unknown source node: {edge.source}"
            )

        if edge.target not in self.nodes:
            raise ValueError(
                f"Unknown target node: {edge.target}"
            )

        self.edges.setdefault(
            edge.source,
            [],
        )

        self.edges[edge.source].append(edge)

    def get_neighbors(
        self,
        node_id: str,
    ) -> list[Edge]:

        return self.edges.get(
            node_id,
            [],
        )


def create_grid(
    start_latitude: float,
    start_longitude: float,
    rows: int,
    columns: int,
    latitude_step: float,
    longitude_step: float,
) -> MarineGraph:

    if rows < 2:
        raise ValueError(
            "rows must be at least 2"
        )

    if columns < 2:
        raise ValueError(
            "columns must be at least 2"
        )

    graph = MarineGraph()

    for row in range(rows):

        for column in range(columns):

            node_id = f"N{row * columns + column + 1}"

            latitude = (
                start_latitude
                + row * latitude_step
            )

            longitude = (
                start_longitude
                + column * longitude_step
            )

            graph.add_node(
                Node(
                    id=node_id,
                    latitude=latitude,
                    longitude=longitude,
                )
            )

    return graph


def _distance(
    a: Node,
    b: Node,
) -> float:

    from .engine import RouteEngine

    return RouteEngine.calculate_distance(
        (a.latitude, a.longitude),
        (b.latitude, b.longitude),
    )


def connect_grid(
    graph: MarineGraph,
    rows: int,
    columns: int,
) -> MarineGraph:

    if rows < 2 or columns < 2:
        raise ValueError(
            "rows and columns must be at least 2"
        )

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),

        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]

    for row in range(rows):

        for column in range(columns):

            source_index = (
                row * columns + column + 1
            )

            source_id = f"N{source_index}"

            source = graph.nodes[source_id]

            for row_delta, column_delta in directions:

                target_row = row + row_delta
                target_column = column + column_delta

                if not (
                    0 <= target_row < rows
                    and
                    0 <= target_column < columns
                ):
                    continue

                target_index = (
                    target_row * columns
                    + target_column
                    + 1
                )

                target_id = f"N{target_index}"

                target = graph.nodes[target_id]

                graph.add_edge(
                    Edge(
                        source=source_id,
                        target=target_id,
                        weight=_distance(
                            source,
                            target,
                        ),
                    )
                )

    return graph


def apply_zone_constraints(
    graph: MarineGraph,
    restricted_zones: list,
) -> MarineGraph:

    if not restricted_zones:
        return graph

    polygons = []

    from .geometry import zone_to_polygon

    for zone in restricted_zones:

        try:
            polygons.append(
                zone_to_polygon(zone)
            )
        except ValueError:
            continue

    for source_id in list(graph.edges):

        source_node = graph.nodes.get(
            source_id
        )

        if source_node is None:
            continue

        valid_edges = []

        for edge in graph.edges[source_id]:

            target_node = graph.nodes.get(
                edge.target
            )

            if target_node is None:
                continue

            coordinates = [
                (
                    source_node.latitude,
                    source_node.longitude,
                ),
                (
                    target_node.latitude,
                    target_node.longitude,
                ),
            ]

            blocked = any(
                route_intersects_polygon(
                    coordinates,
                    polygon,
                )
                for polygon in polygons
            )

            if not blocked:
                valid_edges.append(edge)

        graph.edges[source_id] = valid_edges

    return graph


def apply_risk_constraints(
    graph: MarineGraph,
    routing_risk: dict,
) -> MarineGraph:

    unsafe_nodes = {
        node_id
        for node_id, data in routing_risk.items()
        if not data.get("safe", False)
    }

    for node_id in unsafe_nodes:

        graph.nodes.pop(
            node_id,
            None,
        )

        graph.edges.pop(
            node_id,
            None,
        )

    for node_id in graph.edges:

        graph.edges[node_id] = [
            edge
            for edge in graph.edges[node_id]
            if edge.target not in unsafe_nodes
        ]

    return graph


def path_to_coordinates(
    graph: MarineGraph,
    path: list[str],
) -> list[tuple[float, float]]:

    coordinates = []

    for node_id in path:

        if node_id not in graph.nodes:
            raise ValueError(
                f"Unknown node: {node_id}"
            )

        node = graph.nodes[node_id]

        coordinates.append(
            (
                node.latitude,
                node.longitude,
            )
        )

    return coordinates


def find_nearest_node(
    graph: MarineGraph,
    latitude: float,
    longitude: float,
) -> str:

    if not graph.nodes:
        raise ValueError(
            "Graph contains no nodes"
        )

    from .engine import RouteEngine

    nearest_node_id = None
    shortest_distance = float("inf")

    for node_id, node in graph.nodes.items():

        distance = RouteEngine.calculate_distance(
            (latitude, longitude),
            (
                node.latitude,
                node.longitude,
            ),
        )

        if distance < shortest_distance:

            shortest_distance = distance
            nearest_node_id = node_id

    return nearest_node_id


def create_route_grid(
    start_latitude: float,
    start_longitude: float,
    goal_latitude: float,
    goal_longitude: float,
    rows: int = 10,
    columns: int = 10,
) -> MarineGraph:

    if rows < 2:
        raise ValueError(
            "rows must be at least 2"
        )

    if columns < 2:
        raise ValueError(
            "columns must be at least 2"
        )

    min_lat = min(
        start_latitude,
        goal_latitude,
    )

    min_lon = min(
        start_longitude,
        goal_longitude,
    )

    max_lat = max(
        start_latitude,
        goal_latitude,
    )

    max_lon = max(
        start_longitude,
        goal_longitude,
    )

    latitude_range = max_lat - min_lat
    longitude_range = max_lon - min_lon

    if latitude_range == 0:
        latitude_range = 0.01

    if longitude_range == 0:
        longitude_range = 0.01

    latitude_step = (
        latitude_range / (rows - 1)
    )

    longitude_step = (
        longitude_range / (columns - 1)
    )

    return create_grid(
        start_latitude=min_lat,
        start_longitude=min_lon,
        rows=rows,
        columns=columns,
        latitude_step=latitude_step,
        longitude_step=longitude_step,
    )