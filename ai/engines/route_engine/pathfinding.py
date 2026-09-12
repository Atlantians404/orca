import heapq
import math


def _heuristic(
    graph,
    node_id: str,
    goal_id: str,
) -> float:

    from .engine import RouteEngine

    node = graph.nodes[node_id]
    goal = graph.nodes[goal_id]

    return RouteEngine.calculate_distance(
        (node.latitude, node.longitude),
        (goal.latitude, goal.longitude),
    )


def astar(
    graph,
    start: str,
    goal: str,
) -> tuple[list[str], float]:

    if start not in graph.nodes:
        raise ValueError(
            f"Unknown start node: {start}"
        )

    if goal not in graph.nodes:
        raise ValueError(
            f"Unknown goal node: {goal}"
        )

    open_heap = []

    heapq.heappush(
        open_heap,
        (
            0.0,
            start,
        ),
    )

    came_from = {}

    g_score = {
        start: 0.0
    }

    visited = set()

    while open_heap:

        _, current = heapq.heappop(
            open_heap
        )

        if current in visited:
            continue

        visited.add(current)

        if current == goal:

            path = [current]

            while current in came_from:
                current = came_from[current]
                path.append(current)

            path.reverse()

            return (
                path,
                g_score[goal],
            )

        for edge in graph.get_neighbors(current):

            if edge.target not in graph.nodes:
                continue

            tentative_g = (
                g_score[current]
                + edge.weight
            )

            if tentative_g < g_score.get(
                edge.target,
                float("inf"),
            ):

                came_from[edge.target] = current

                g_score[edge.target] = tentative_g

                f_score = (
                    tentative_g
                    + _heuristic(
                        graph,
                        edge.target,
                        goal,
                    )
                )

                heapq.heappush(
                    open_heap,
                    (
                        f_score,
                        edge.target,
                    ),
                )

    raise ValueError(
        "No route exists between the requested nodes."
    )


def dijkstra(
    graph,
    start: str,
    goal: str,
) -> tuple[list[str], float]:

    if start not in graph.nodes:
        raise ValueError(
            f"Unknown start node: {start}"
        )

    if goal not in graph.nodes:
        raise ValueError(
            f"Unknown goal node: {goal}"
        )

    heap = [
        (0.0, start)
    ]

    distances = {
        start: 0.0
    }

    previous = {}

    while heap:

        distance, current = heapq.heappop(
            heap
        )

        if distance > distances.get(
            current,
            float("inf"),
        ):
            continue

        if current == goal:

            path = [current]

            while current in previous:
                current = previous[current]
                path.append(current)

            path.reverse()

            return (
                path,
                distance,
            )

        for edge in graph.get_neighbors(current):

            new_distance = (
                distance
                + edge.weight
            )

            if new_distance < distances.get(
                edge.target,
                float("inf"),
            ):

                distances[edge.target] = new_distance
                previous[edge.target] = current

                heapq.heappush(
                    heap,
                    (
                        new_distance,
                        edge.target,
                    ),
                )

    raise ValueError(
        "No route exists between the requested nodes."
    )


def calculate_path_distance(
    graph,
    path: list[str],
) -> float:

    if len(path) < 2:
        return 0.0

    total = 0.0

    for source, target in zip(
        path,
        path[1:],
    ):

        edge = next(
            (
                edge
                for edge in graph.get_neighbors(
                    source
                )
                if edge.target == target
            ),
            None,
        )

        if edge is None:
            raise ValueError(
                f"No edge between {source} and {target}"
            )

        total += edge.weight

    return total


def generate_candidate_paths(
    graph,
    start: str,
    goal: str,
    max_routes: int = 3,
) -> list[tuple[list[str], float]]:

    if max_routes < 1:
        raise ValueError(
            "max_routes must be at least 1"
        )

    candidates = []

    first_path, first_distance = astar(
        graph,
        start,
        goal,
    )

    candidates.append(
        (
            first_path,
            first_distance,
        )
    )

    if max_routes == 1:
        return candidates

    blocked_edges = set()

    for _ in range(max_routes - 1):

        previous_path = candidates[-1][0]

        if len(previous_path) < 2:
            break

        for source, target in zip(
            previous_path,
            previous_path[1:],
        ):

            blocked_edges.add(
                (source, target)
            )

            blocked_edges.add(
                (target, source)
            )

        original_edges = {}

        for source in graph.edges:

            original_edges[source] = list(
                graph.edges[source]
            )

        for source, target in blocked_edges:

            if source not in graph.edges:
                continue

            graph.edges[source] = [
                edge
                for edge in graph.edges[source]
                if edge.target != target
            ]

        try:

            path, distance = astar(
                graph,
                start,
                goal,
            )

        except ValueError:
            path = None
            distance = None

        finally:

            graph.edges = original_edges

        if path is None:
            break

        if any(
            path == existing_path
            for existing_path, _ in candidates
        ):
            break

        candidates.append(
            (
                path,
                distance,
            )
        )

    return candidates