import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )
)

from ai.engines.risk_engine.route_select import select_best_route

k7_input = {
    "route": {
        "coastal_reference": "KARPAKAM",
        "start": {
            "latitude": 13.0827,
            "longitude": 80.2707
        },
        "destination": {
            "latitude": 13.4500,
            "longitude": 80.3200
        },
        "candidate_routes": [
    {
        "route_id": "route_001",
        "waypoints": [
            {"node_id": "node_001", "latitude": 13.1500, "longitude": 80.2800},
            {"node_id": "node_002", "latitude": 13.2500, "longitude": 80.2900},
            {"node_id": "node_003", "latitude": 13.3500, "longitude": 80.3100}
        ]
    },
    {
        "route_id": "route_002",
        "waypoints": [
            {"node_id": "node_101", "latitude": 13.1200, "longitude": 80.2000},
            {"node_id": "node_102", "latitude": 13.2000, "longitude": 80.1500},
            {"node_id": "node_103", "latitude": 13.3000, "longitude": 80.1800},
            {"node_id": "node_104", "latitude": 13.4000, "longitude": 80.2500}
        ]
    },
    {
        "route_id": "route_003",
        "waypoints": [
            {"node_id": "node_201", "latitude": 13.1300, "longitude": 80.2300},
            {"node_id": "node_202", "latitude": 13.2300, "longitude": 80.2600},
            {"node_id": "node_203", "latitude": 13.3700, "longitude": 80.2900}
        ]
    }
]
    },
    "time": "2026-09-07T06:00:00"
}

mock_risk_data = {
    "node_001": {"risk_score": 48.7},
    "node_002": {"risk_score": 52.3},
    "node_003": {"risk_score": 55.8},

    "node_101": {"risk_score": 18.6},
    "node_102": {"risk_score": 22.4},
    "node_103": {"risk_score": 25.9},
    "node_104": {"risk_score": 21.7},

    "node_201": {"risk_score": 42.8},
    "node_202": {"risk_score": 46.5},
    "node_203": {"risk_score": 50.2}
}
result = select_best_route(k7_input, mock_risk_data)

print("BEST ROUTE")
print(result)