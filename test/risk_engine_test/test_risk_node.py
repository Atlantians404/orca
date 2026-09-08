import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ai.engines.risk_engine.risk_node import risk_engine_node

with open("test/risk_engine_test/test_case3.json", "r") as f:
    agent_data = json.load(f)

state = {
    "agent_data": agent_data
}

result = asyncio.run(risk_engine_node(state))

print("RISK NODE RESULT")
print(json.dumps(result, indent=2))