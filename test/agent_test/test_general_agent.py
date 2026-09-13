import pytest

from ai.agents.general_agent.general_agent import general_agent


@pytest.mark.asyncio
async def test_general_agent_temperature():

    result = await general_agent.ainvoke(
        {
            "messages": [
                (
                    "user",
                    "What is the temperature at "
                    "latitude 13.0827 longitude 80.2707 "
                    "at 2026-09-05T17:00?"
                )
            ]
        }
    )

    print("\n====================================")
    print("GENERAL AGENT")
    print("====================================")

    for message in result["messages"]:
        print("\nMESSAGE:")
        print(message)

    final_message = result["messages"][-1]

    print("\nFINAL RESPONSE:")
    print(final_message.content)

    assert final_message.content


@pytest.mark.asyncio
async def test_general_agent_sea_temperature():

    result = await general_agent.ainvoke(
        {
            "messages": [
                (
                    "user",
                    "What is the sea surface temperature at "
                    "latitude 13.0827 longitude 80.2707 "
                    "at 2026-09-05T17:00?"
                )
            ]
        }
    )

    print("\n====================================")
    print("SEA TEMPERATURE TEST")
    print("====================================")

    for message in result["messages"]:
        print("\nMESSAGE:")
        print(message)

    final_message = result["messages"][-1]

    print("\nFINAL RESPONSE:")
    print(final_message.content)

    assert final_message.content