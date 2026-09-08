from math import radians, sin, cos, sqrt, atan2

RISK_WEIGHT = 0.70
DISTANCE_WEIGHT = 0.30
SAFE_RISK_LIMIT = 60.0

def haversine(lat1, lon1, lat2, lon2):
    earth_radius = 6371.0
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    dlat = lat2 - lat1
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return earth_radius * 2 * atan2(sqrt(a), sqrt(1 - a))

def calculate_route_distance(route, start, destination):
    points = [start] + route["waypoints"] + [destination]
    total_distance = 0.0

    for i in range(len(points) - 1):
        total_distance += haversine(
            points[i]["latitude"],
            points[i]["longitude"],
            points[i + 1]["latitude"],
            points[i + 1]["longitude"]
        )

    return round(total_distance, 2)

def calculate_route_risk(route, risk_data):
    risk_scores = []

    for waypoint in route["waypoints"]:
        node_id = waypoint["node_id"]
        risk_scores.append(risk_data[node_id]["risk_score"])

    if not risk_scores:
        return 0.0, 0.0, True

    average_risk = sum(risk_scores) / len(risk_scores)
    maximum_risk = max(risk_scores)
    safe = maximum_risk <= SAFE_RISK_LIMIT

    return round(average_risk, 2), maximum_risk, safe

def calculate_route_score(risk_score, distance, maximum_distance):
    if maximum_distance == 0:
        distance_score = 0.0
    else:
        distance_score = (distance / maximum_distance) * 100

    route_score = (
        risk_score * RISK_WEIGHT
        + distance_score * DISTANCE_WEIGHT
    )

    return round(route_score, 2)

def select_best_route(data, risk_data):
    route_data = data["route"]
    start = route_data["start"]
    destination = route_data["destination"]
    routes = route_data["candidate_routes"]

    evaluated_routes = []

    for route in routes:
        distance = calculate_route_distance(
            route,
            start,
            destination
        )

        risk_score, maximum_risk, safe = calculate_route_risk(
            route,
            risk_data
        )

        evaluated_routes.append({
            "route": route,
            "distance_km": distance,
            "risk_score": risk_score,
            "max_risk_score": maximum_risk,
            "safe": safe
        })

    if not evaluated_routes:
        return None

    maximum_distance = max(
        route["distance_km"]
        for route in evaluated_routes
    )

    safe_routes = [
        route
        for route in evaluated_routes
        if route["safe"]
    ]

    routes_to_compare = safe_routes or evaluated_routes

    for route in routes_to_compare:
        route["route_score"] = calculate_route_score(
            route["risk_score"],
            route["distance_km"],
            maximum_distance
        )

    best_route = min(
        routes_to_compare,
        key=lambda route: route["route_score"]
    )

    return best_route["route"]