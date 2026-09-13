import sys
import os
import asyncio

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

k7_input={
  "time": "2026-09-05T08:00:00",
  "nodes": [
    {"node_id": "N1", "latitude": 13.050, "longitude": 80.250},
    {"node_id": "N2", "latitude": 13.052, "longitude": 80.252},
    {"node_id": "N3", "latitude": 13.054, "longitude": 80.254},
    {"node_id": "N4", "latitude": 13.056, "longitude": 80.256},
    {"node_id": "N5", "latitude": 13.058, "longitude": 80.258},
    {"node_id": "N6", "latitude": 13.060, "longitude": 80.260},
    {"node_id": "N7", "latitude": 13.062, "longitude": 80.262},
    {"node_id": "N8", "latitude": 13.064, "longitude": 80.264},
    {"node_id": "N9", "latitude": 13.066, "longitude": 80.266},
    {"node_id": "N10", "latitude": 13.068, "longitude": 80.268},
    {"node_id": "N11", "latitude": 13.070, "longitude": 80.270},
    {"node_id": "N12", "latitude": 13.072, "longitude": 80.272},
    {"node_id": "N13", "latitude": 13.074, "longitude": 80.274},
    {"node_id": "N14", "latitude": 13.076, "longitude": 80.276},
    {"node_id": "N15", "latitude": 13.078, "longitude": 80.278},
    {"node_id": "N16", "latitude": 13.080, "longitude": 80.280},
    {"node_id": "N17", "latitude": 13.082, "longitude": 80.282},
    {"node_id": "N18", "latitude": 13.084, "longitude": 80.284},
    {"node_id": "N19", "latitude": 13.086, "longitude": 80.286},
    {"node_id": "N20", "latitude": 13.088, "longitude": 80.288},
    {"node_id": "N21", "latitude": 13.090, "longitude": 80.290},
    {"node_id": "N22", "latitude": 13.092, "longitude": 80.292},
    {"node_id": "N23", "latitude": 13.094, "longitude": 80.294},
    {"node_id": "N24", "latitude": 13.096, "longitude": 80.296},
    {"node_id": "N25", "latitude": 13.098, "longitude": 80.298},
    {"node_id": "N26", "latitude": 13.100, "longitude": 80.300},
    {"node_id": "N27", "latitude": 13.102, "longitude": 80.302},
    {"node_id": "N28", "latitude": 13.104, "longitude": 80.304},
    {"node_id": "N29", "latitude": 13.106, "longitude": 80.306},
    {"node_id": "N30", "latitude": 13.108, "longitude": 80.308},
    {"node_id": "N31", "latitude": 13.110, "longitude": 80.310},
    {"node_id": "N32", "latitude": 13.112, "longitude": 80.312},
    {"node_id": "N33", "latitude": 13.114, "longitude": 80.314},
    {"node_id": "N34", "latitude": 13.116, "longitude": 80.316},
    {"node_id": "N35", "latitude": 13.118, "longitude": 80.318},
    {"node_id": "N36", "latitude": 13.120, "longitude": 80.320},
    {"node_id": "N37", "latitude": 13.122, "longitude": 80.322},
    {"node_id": "N38", "latitude": 13.124, "longitude": 80.324},
    {"node_id": "N39", "latitude": 13.126, "longitude": 80.326},
    {"node_id": "N40", "latitude": 13.128, "longitude": 80.328},
    {"node_id": "N41", "latitude": 13.130, "longitude": 80.330},
    {"node_id": "N42", "latitude": 13.132, "longitude": 80.332},
    {"node_id": "N43", "latitude": 13.134, "longitude": 80.334},
    {"node_id": "N44", "latitude": 13.136, "longitude": 80.336},
    {"node_id": "N45", "latitude": 13.138, "longitude": 80.338},
    {"node_id": "N46", "latitude": 13.140, "longitude": 80.340},
    {"node_id": "N47", "latitude": 13.142, "longitude": 80.342},
    {"node_id": "N48", "latitude": 13.144, "longitude": 80.344},
    {"node_id": "N49", "latitude": 13.146, "longitude": 80.346},
    {"node_id": "N50", "latitude": 13.148, "longitude": 80.348}
  ]
}

print("\nTEST STARTED\n")

result = asyncio.run(process_grid(k7_input))

print("RISK HELPER RESULT\n")

for node_result in result:
    print(node_result)

print("\nTEST FINISHED")