import heapq


from .graph import MarineGraph
from .engine import RouteEngine


def dijkstra(
    graph: MarineGraph,
    start: str,
    goal: str
) -> tuple[list[str], float]:

    distances = {
        node_id: float("inf")
        for node_id in graph.nodes
    }

    previous = {
        node_id: None
        for node_id in graph.nodes
    }

    distances[start] = 0

    priority_queue = [
        (0, start)
    ]

    while priority_queue:

        current_distance, current_node = (
            heapq.heappop(priority_queue)
        )

        if current_node == goal:
            break

        if current_distance > distances[current_node]:
            continue

        for edge in graph.get_neighbors(current_node):

            new_distance = (
                current_distance
                + edge.weight
            )

            if new_distance < distances[edge.target]:

                distances[edge.target] = new_distance

                previous[edge.target] = current_node

                heapq.heappush(
                    priority_queue,
                    (
                        new_distance,
                        edge.target
                    )
                )

    if distances[goal] == float("inf"):
        raise ValueError(
            f"No path found from {start} to {goal}"
        )

    path = []

    current = goal

    while current is not None:

        path.append(current)

        current = previous[current]

    path.reverse()

    return path, distances[goal]

def astar(
    graph: MarineGraph,
    start: str,
    goal: str
) -> tuple[list[str], float]:

    distances = {
        node_id: float("inf")
        for node_id in graph.nodes
    }

    previous = {
        node_id: None
        for node_id in graph.nodes
    }

    distances[start] = 0

    start_node = graph.nodes[start]
    goal_node = graph.nodes[goal]

    heuristic = RouteEngine.calculate_distance(
        (
            start_node.latitude,
            start_node.longitude
        ),
        (
            goal_node.latitude,
            goal_node.longitude
        )
    )

    priority_queue = [
        (heuristic, start)
    ]

    while priority_queue:

        _, current_node = heapq.heappop(
            priority_queue
        )

        if current_node == goal:
            break

        current_distance = distances[current_node]

        for edge in graph.get_neighbors(current_node):

            new_distance = (
                current_distance
                + edge.weight
            )

            if new_distance < distances[edge.target]:

                distances[edge.target] = new_distance

                previous[edge.target] = current_node

                neighbor = graph.nodes[edge.target]

                heuristic = RouteEngine.calculate_distance(
                    (
                        neighbor.latitude,
                        neighbor.longitude
                    ),
                    (
                        goal_node.latitude,
                        goal_node.longitude
                    )
                )

                priority = (
                    new_distance
                    + heuristic
                )

                heapq.heappush(
                    priority_queue,
                    (
                        priority,
                        edge.target
                    )
                )

    if distances[goal] == float("inf"):
        raise ValueError(
            f"No path found from {start} to {goal}"
        )

    path = []

    current = goal

    while current is not None:

        path.append(current)

        current = previous[current]

    path.reverse()

    return path, distances[goal]

