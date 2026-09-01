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

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        self.edges.setdefault(node.id, [])

    def add_edge(self, edge: Edge):
        self.edges.setdefault(edge.source, [])
        self.edges[edge.source].append(edge)

    def get_neighbors(self, node_id: str) -> list[Edge]:
        return self.edges.get(node_id, [])


def create_grid(
    start_latitude: float,
    start_longitude: float,
    rows: int,
    columns: int,
    latitude_step: float,
    longitude_step: float
) -> MarineGraph:
    """
    Create a geographic grid of nodes.

    Each node represents a location
    in the marine area.
    """

    graph = MarineGraph()

    for row in range(rows):

        for column in range(columns):

            node_id = (
                f"N{row * columns + column + 1}"
            )

            latitude = round(
                start_latitude
                + row * latitude_step,
                6
            )

            longitude = round(
                start_longitude
                + column * longitude_step,
                6
            )

            node = Node(
                id=node_id,
                latitude=latitude,
                longitude=longitude
            )

            graph.add_node(node)

    return graph


def connect_grid(
    graph: MarineGraph,
    rows: int,
    columns: int
) -> MarineGraph:
    """
    Connect adjacent nodes in the grid.

    Connections:
        - horizontal
        - vertical
        - diagonal

    Edge weight = Haversine distance in km.
    """

    from .engine import RouteEngine

    def add_connection(
        source_id: str,
        target_id: str
    ):
        source_node = graph.nodes[source_id]
        target_node = graph.nodes[target_id]

        distance = RouteEngine.calculate_distance(
            (
                source_node.latitude,
                source_node.longitude
            ),
            (
                target_node.latitude,
                target_node.longitude
            )
        )

        graph.add_edge(
            Edge(
                source=source_id,
                target=target_id,
                weight=distance
            )
        )

        graph.add_edge(
            Edge(
                source=target_id,
                target=source_id,
                weight=distance
            )
        )

    for row in range(rows):

        for column in range(columns):

            current_id = (
                f"N{row * columns + column + 1}"
            )

            # ------------------------------------------
            # Horizontal: right
            # ------------------------------------------

            if column < columns - 1:

                right_id = (
                    f"N{row * columns + column + 2}"
                )

                add_connection(
                    current_id,
                    right_id
                )

            # ------------------------------------------
            # Vertical: below
            # ------------------------------------------

            if row < rows - 1:

                below_id = (
                    f"N{(row + 1) * columns + column + 1}"
                )

                add_connection(
                    current_id,
                    below_id
                )

            # ------------------------------------------
            # Diagonal: down-right
            # ------------------------------------------

            if (
                row < rows - 1
                and column < columns - 1
            ):

                diagonal_id = (
                    f"N{(row + 1) * columns + column + 2}"
                )

                add_connection(
                    current_id,
                    diagonal_id
                )

            # ------------------------------------------
            # Diagonal: down-left
            # ------------------------------------------

            if (
                row < rows - 1
                and column > 0
            ):

                diagonal_id = (
                    f"N{(row + 1) * columns + column}"
                )

                add_connection(
                    current_id,
                    diagonal_id
                )

    return graph


def apply_zone_constraints(
    graph: MarineGraph,
    restricted_polygon
) -> MarineGraph:
    """
    Remove graph edges that intersect
    a restricted polygon.
    """

    for source_id in list(graph.edges.keys()):

        valid_edges = []

        source_node = graph.nodes[source_id]

        for edge in graph.edges[source_id]:

            target_node = graph.nodes[edge.target]

            route_segment = create_linestring(
                [
                    (
                        source_node.latitude,
                        source_node.longitude
                    ),
                    (
                        target_node.latitude,
                        target_node.longitude
                    )
                ]
            )

            if not route_intersects_polygon(
                route_segment,
                restricted_polygon
            ):
                valid_edges.append(edge)

        graph.edges[source_id] = valid_edges

    return graph


def path_to_coordinates(
    graph: MarineGraph,
    path: list[str]
) -> list[tuple[float, float]]:
    """
    Convert a list of node IDs into
    (latitude, longitude) coordinates.
    """

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
                node.longitude
            )
        )

    return coordinates


def find_nearest_node(
    graph: MarineGraph,
    latitude: float,
    longitude: float
) -> str:
    """
    Find the graph node closest to
    a geographic coordinate.
    """

    if not graph.nodes:
        raise ValueError(
            "Graph contains no nodes"
        )

    nearest_node_id = None
    shortest_distance = float("inf")

    from .engine import RouteEngine

    for node_id, node in graph.nodes.items():

        distance = RouteEngine.calculate_distance(
            (latitude, longitude),
            (
                node.latitude,
                node.longitude
            )
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
    """
    Create a geographic grid covering the area
    between the start and destination.
    """

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
        goal_latitude
    )

    max_lat = max(
        start_latitude,
        goal_latitude
    )

    min_lon = min(
        start_longitude,
        goal_longitude
    )

    max_lon = max(
        start_longitude,
        goal_longitude
    )

    latitude_range = max_lat - min_lat
    longitude_range = max_lon - min_lon

    # Prevent zero-size grids
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