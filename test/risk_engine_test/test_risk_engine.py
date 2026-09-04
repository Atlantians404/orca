import sys
import os

# Add ORCA project root to Python path
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

import json

from ai.engines.risk_engine.main import run_risk_engine


print("TEST FILE STARTED")


with open(
    "test/risk_engine_test/test_case1.json",
    "r"
) as file:

    agent_data = json.load(file)


print("JSON LOADED")


result = run_risk_engine(
    agent_data
)


print("ENGINE EXECUTED")

print("\n==============================")
print("RISK ENGINE RESULT")
print("==============================")


print(json.dumps(
    result,
    indent=2
))


print("==============================")
print("TEST FINISHED")