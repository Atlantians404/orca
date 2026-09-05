import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from ai.tools.risk_helper import process_grid


k7_input = {
    "nodes": [
        {"node_id": "N1", "latitude": 13.08, "longitude": 80.27},
        {"node_id": "N2", "latitude": 13.09, "longitude": 80.28},
        {"node_id": "N3", "latitude": 13.10, "longitude": 80.29},
        {"node_id": "N4", "latitude": 13.11, "longitude": 80.30},
        {"node_id": "N5", "latitude": 13.12, "longitude": 80.31},
        {"node_id": "N6", "latitude": 13.13, "longitude": 80.32},
        {"node_id": "N7", "latitude": 13.14, "longitude": 80.33},
        {"node_id": "N8", "latitude": 13.15, "longitude": 80.34},
        {"node_id": "N9", "latitude": 13.16, "longitude": 80.35},
        {"node_id": "N10", "latitude": 13.17, "longitude": 80.36}
    ],
    "time": "2026-09-05T08:00:00"
}


print("\nTEST STARTED\n")

result = process_grid(k7_input)

print("RISK HELPER RESULT\n")

for node_result in result:
    print(node_result)

print("\nTEST FINISHED")