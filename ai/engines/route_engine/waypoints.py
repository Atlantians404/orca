from .graph import MarineGraph
from .schemas import Waypoint


def generate_waypoints(
    graph: MarineGraph,
    path: list[str]
) -> list[Waypoint]:
    """
    Convert a graph path into intermediate waypoints.

    The first node represents the start location
    and the last node represents the destination/PFZ.

    Only intermediate nodes are returned as waypoints.
    """

    if not path:
        raise ValueError(
            "Path cannot be empty"
        )

    if len(path) <= 2:
        return []

    waypoints = []

    for node_id in path[1:-1]:

        if node_id not in graph.nodes:
            raise ValueError(
                f"Unknown node: {node_id}"
            )

        node = graph.nodes[node_id]

        waypoints.append(
            Waypoint(
                latitude=node.latitude,
                longitude=node.longitude
            )
        )

    return waypoints


def generate_waypoints_from_coordinates(
    coordinates: list[tuple[float, float]]
) -> list[Waypoint]:
    """
    Convert a list of coordinates into intermediate
    waypoints.

    Coordinates are:
        (latitude, longitude)

    The first coordinate is the start and the last
    coordinate is the destination.
    """

    if not coordinates:
        raise ValueError(
            "Coordinates cannot be empty"
        )

    if len(coordinates) <= 2:
        return []

    return [
        Waypoint(
            latitude=latitude,
            longitude=longitude
        )
        for latitude, longitude
        in coordinates[1:-1]
    ]


def validate_waypoints(
    waypoints: list[Waypoint]
) -> bool:
    """
    Validate that all waypoints contain valid
    latitude and longitude values.
    """

    for waypoint in waypoints:

        if not -90 <= waypoint.latitude <= 90:
            return False

        if not -180 <= waypoint.longitude <= 180:
            return False

    return True