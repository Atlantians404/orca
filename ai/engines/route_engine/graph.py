from dataclasses import dataclass
from .engine import RouteEngine


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

    Each node represents a location in the marine area.
    """

    graph = MarineGraph()

    for row in range(rows):

        for column in range(columns):

            node_id = f"N{row * columns + column + 1}"

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
    Connect horizontally and vertically adjacent
    nodes in the grid.

    Edge weight = Haversine distance in km.
    """

    for row in range(rows):

        for column in range(columns):

            current_id = f"N{row * columns + column + 1}"

            current_node = graph.nodes[current_id]

            # Connect to the node on the right
            if column < columns - 1:

                right_id = (
                    f"N{row * columns + column + 2}"
                )

                right_node = graph.nodes[right_id]

                distance = RouteEngine.calculate_distance(
                    (
                        current_node.latitude,
                        current_node.longitude
                    ),
                    (
                        right_node.latitude,
                        right_node.longitude
                    )
                )

                graph.add_edge(
                    Edge(
                        source=current_id,
                        target=right_id,
                        weight=distance
                    )
                )

                graph.add_edge(
                    Edge(
                        source=right_id,
                        target=current_id,
                        weight=distance
                    )
                )

            # Connect to the node below
            if row < rows - 1:

                below_id = (
                    f"N{(row + 1) * columns + column + 1}"
                )

                below_node = graph.nodes[below_id]

                distance = RouteEngine.calculate_distance(
                    (
                        current_node.latitude,
                        current_node.longitude
                    ),
                    (
                        below_node.latitude,
                        below_node.longitude
                    )
                )

                graph.add_edge(
                    Edge(
                        source=current_id,
                        target=below_id,
                        weight=distance
                    )
                )

                graph.add_edge(
                    Edge(
                        source=below_id,
                        target=current_id,
                        weight=distance
                    )
                )

    return graph

