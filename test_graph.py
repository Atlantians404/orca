import asyncio

from ai.engines.data_collection_engine.data_collection_engine import (
    data_collection_engine
)

from ai.schemas.location import Location
from ai.schemas.time import TimeContext, TimeSlot


async def main():

    state = {
        "prompt": "Find marine conditions near my nearest PFZ",

        "location": Location(
            latitude=13.08,
            longitude=80.27
        ),

        "time_context": TimeContext(
            slots=[
                TimeSlot(
                    date="2026-08-30",
                    start_time="08:00",
                    end_time=None
                )
            ]
        ),

        "pfz_candidates": [
            {
                "name": "PFZ11",
                "coastal_reference": "Chinna Neelankarai",
                "latitude": 12.916389,
                "longitude": 80.455833,
                "distance_from_source_km": 27.14,
                "direction": "SE",
                "depth_m": {
                    "min": 64,
                    "max": 69
                }
            }
        ],

        "agent_data": {}
    }

    result = await data_collection_engine(state)

    print("\n" + "=" * 60)
    print("DATA COLLECTION ENGINE TEST")
    print("=" * 60)

    print("\nPFZ:")
    print(result["agent_data"].keys())

    for pfz_name, time_data in result["agent_data"].items():

        print(f"\nPFZ: {pfz_name}")

        for collection_time, data in time_data.items():

            print(f"\nTime: {collection_time}")

            print("\nMarine:")
            print(data["marine"])

            print("\nWeather:")
            print(data["weather"])

            print("\nGeo:")
            print(data["geo"])


if __name__ == "__main__":
    asyncio.run(main())