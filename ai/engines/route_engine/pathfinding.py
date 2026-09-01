import heapq

from .graph import MarineGraph


def dijkstra(
    graph: MarineGraph,
    start: str,
    goal: str
) -> tuple[list[str], float]:
    """
    Find the shortest path using Dijkstra's algorithm.
    """

    if start not in graph.nodes:
        raise ValueError(
            f"Unknown start node: {start}"
        )

    if goal not in graph.nodes:
        raise ValueError(
            f"Unknown goal node: {goal}"
        )

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
    """
    Find the shortest path using A*.
    """

    if start not in graph.nodes:
        raise ValueError(
            f"Unknown start node: {start}"
        )

    if goal not in graph.nodes:
        raise ValueError(
            f"Unknown goal node: {goal}"
        )

    from .engine import RouteEngine

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


# =========================================================
# PATH DISTANCE
# =========================================================

def calculate_path_distance(
    graph: MarineGraph,
    path: list[str]
) -> float:
    """
    Calculate the total distance of a graph path.
    """

    if len(path) < 2:
        return 0.0

    total_distance = 0.0

    for source, target in zip(
        path,
        path[1:]
    ):

        edge = next(
            (
                edge
                for edge in graph.get_neighbors(source)
                if edge.target == target
            ),
            None
        )

        if edge is None:
            raise ValueError(
                f"No edge between {source} and {target}"
            )

        total_distance += edge.weight

    return total_distance


# =========================================================
# CANDIDATE PATH GENERATION
# =========================================================

def generate_candidate_paths(
    graph: MarineGraph,
    start: str,
    goal: str,
    max_routes: int = 3
) -> list[tuple[list[str], float]]:
    """
    Generate multiple candidate paths.

    The first route is the shortest A* route.

    Additional routes are created by temporarily
    removing edges from the shortest path and
    running A* again.

    Returns:
        [
            (path, distance),
            (path, distance),
            ...
        ]
    """

    if max_routes < 1:
        raise ValueError(
            "max_routes must be at least 1"
        )

    if start not in graph.nodes:
        raise ValueError(
            f"Unknown start node: {start}"
        )

    if goal not in graph.nodes:
        raise ValueError(
            f"Unknown goal node: {goal}"
        )

    # ---------------------------------------------
    # First route: shortest A* route
    # ---------------------------------------------

    first_path, first_distance = astar(
        graph,
        start,
        goal
    )

    candidates = [
        (
            first_path,
            first_distance
        )
    ]

    seen_paths = {
        tuple(first_path)
    }

    # ---------------------------------------------
    # Work on a copy of the graph
    # ---------------------------------------------

    original_edges = {
        node_id: list(edges)
        for node_id, edges
        in graph.edges.items()
    }

    try:

        # -----------------------------------------
        # Generate alternatives
        # -----------------------------------------

        for _ in range(max_routes - 1):

            previous_path = candidates[-1][0]

            if len(previous_path) <= 2:
                break

            alternative_found = False

            # Try removing different edges from
            # the previous route.
            for index in range(
                len(previous_path) - 1
            ):

                source = previous_path[index]
                target = previous_path[index + 1]

                # Remove the edge in both directions
                graph.edges[source] = [
                    edge
                    for edge in graph.edges[source]
                    if edge.target != target
                ]

                graph.edges[target] = [
                    edge
                    for edge in graph.edges[target]
                    if edge.target != source
                ]

                try:

                    new_path, new_distance = astar(
                        graph,
                        start,
                        goal
                    )

                    path_key = tuple(new_path)

                    if path_key not in seen_paths:

                        candidates.append(
                            (
                                new_path,
                                new_distance
                            )
                        )

                        seen_paths.add(
                            path_key
                        )

                        alternative_found = True

                        # Restore graph before
                        # trying to generate the
                        # next candidate.
                        graph.edges = {
                            node_id: list(edges)
                            for node_id, edges
                            in original_edges.items()
                        }

                        break

                except ValueError:
                    pass

                # Restore the removed edge
                graph.edges = {
                    node_id: list(edges)
                    for node_id, edges
                    in original_edges.items()
                }

            if not alternative_found:
                break

    finally:

        # Always restore original graph
        graph.edges = {
            node_id: list(edges)
            for node_id, edges
            in original_edges.items()
        }

    return candidates