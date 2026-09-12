import asyncio

from ai.agent_state import AgentState
from ai.engines.risk_engine.risk_node import risk_engine_node


async def test_risk_engine():

    print("\n")
    print("=" * 70)
    print("RISK ENGINE TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Data collected from your Data Collection Agent
    # --------------------------------------------------------

    agent_data = {
        "Egattur Karikattukuppam": {
            "2026-09-13 12:00": {
                "marine": {
                    "wave_height": 0.94,
                    "wave_period": 7.9,
                    "wave_direction": 148,
                    "swell_wave_height": 0.72,
                    "swell_wave_period": 7.65,
                    "swell_wave_direction": 145,
                    "ocean_current_velocity": 2.5,
                    "ocean_current_direction": 4,
                    "sea_surface_temperature": 29.5,
                    "sea_level_height_msl": 0.4,
                    "marine_warning": "None",
                },
                "weather": {
                    "wind_speed": 22.1,
                    "wind_direction": 159,
                    "visibility": 15940.0,
                    "precipitation": 0.0,
                    "lightning": False,
                    "condition": "Overcast",
                },
                "geo": {
                    "latitude": 13.371389,
                    "longitude": 80.434167,
                    "restricted_area": False,
                    "protected_area": False,
                },
            }
        }
    }

    # --------------------------------------------------------
    # Build AgentState
    # --------------------------------------------------------

    state: AgentState = {
        "agent_data": agent_data,
        "workflow_status": "IN_PROGRESS",
    }

    # --------------------------------------------------------
    # Execute Risk Engine Node
    # --------------------------------------------------------

    result = await risk_engine_node(state)

    # --------------------------------------------------------
    # Print result
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("RISK RESULT")
    print("=" * 70)

    print(result.get("risk_result"))

    # --------------------------------------------------------
    # Assertions
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("RUNNING ASSERTIONS")
    print("=" * 70)

    # Risk result must exist
    assert "risk_result" in result, (
        "risk_result missing from node output"
    )

    risk_result = result["risk_result"]

    assert risk_result is not None, (
        "risk_result is None"
    )

    # Workflow status
    assert result["workflow_status"] == "IN_PROGRESS"

    print("\n✅ risk_result exists")
    print("✅ workflow_status is correct")

    print("\n")
    print("=" * 70)
    print("✅ RISK ENGINE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_risk_engine())