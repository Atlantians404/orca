from .schemas import Waypoint


def generate_waypoints(
    graph,
    path: list[str],
) -> list[Waypoint]:

    waypoints = []

    for node_id in path:

        if node_id not in graph.nodes:
            raise ValueError(
                f"Unknown node: {node_id}"
            )

        node = graph.nodes[node_id]

        waypoints.append(
            Waypoint(
                node_id=node.id,
                latitude=node.latitude,
                longitude=node.longitude,
            )
        )

    return waypoints