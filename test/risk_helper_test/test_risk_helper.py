import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ai.tools.risk_helper import build_routing_risk

test_data = [
    {"node_id": "N1", "risk_score": 20},
    {"node_id": "N2", "risk_score": 60},
    {"node_id": "N3", "risk_score": 60.1},
    {"node_id": "N4", "risk_score": 80}
]

result = build_routing_risk(test_data)

print(result)