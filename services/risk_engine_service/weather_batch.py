import asyncio
import httpx

from api.weather.weather import (
    get_open_meteo_data,
    weather_condition_from_code,
    is_thunderstorm,
)


BATCH_SIZE = 20
BATCH_DELAY = 1


def coordinate_key(node):
    return (
        round(float(node["latitude"]), 4),
        round(float(node["longitude"]), 4)
    )


async def get_weather_data_batch(nodes, time):
    if nodes:
        print("First node:", nodes[0])

    if not nodes:
        return {}

    results = {}

    # -----------------------------------------------------
    # Remove duplicate coordinates
    # -----------------------------------------------------

    unique_nodes = {}

    for node in nodes:

        key = coordinate_key(node)

        if key not in unique_nodes:
            unique_nodes[key] = node

    unique_nodes = list(
        unique_nodes.values()
    )

    print(
        f"[WEATHER BATCH] "
        f"Fetching {len(unique_nodes)} coordinates"
    )

    # -----------------------------------------------------
    # HTTP CLIENT
    # -----------------------------------------------------

    async with httpx.AsyncClient(
        timeout=15
    ) as client:

        # -------------------------------------------------
        # Process batches
        # -------------------------------------------------

        for start in range(
            0,
            len(unique_nodes),
            BATCH_SIZE
        ):

            batch = unique_nodes[
                start:start + BATCH_SIZE
            ]

            # -------------------------------------------------
            # Fetch weather concurrently
            # -------------------------------------------------

            tasks = []

            for node in batch:

                tasks.append(
                    get_open_meteo_data(
                        latitude=node["latitude"],
                        longitude=node["longitude"],
                        weather_time=time
                    )
                )

            weather_responses = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )

            # -------------------------------------------------
            # Process results
            # -------------------------------------------------

            for node, weather_data in zip(
                batch,
                weather_responses
            ):

                key = coordinate_key(node)

                if isinstance(
                    weather_data,
                    Exception
                ):

                    print(
                        f"[WEATHER BATCH] "
                        f"Failed for {node['node_id']}: "
                        f"{weather_data}"
                    )

                    results[key] = {}

                    continue

                if not weather_data:

                    results[key] = {}

                    continue

                # -------------------------------------------------
                # SAME FORMAT EXPECTED BY RISK ENGINE
                # -------------------------------------------------

                weather_code = weather_data.get(
                    "weather_code"
                )

                results[key] = {

                    "wind_speed": weather_data.get(
                        "wind_speed"
                    ),

                    "wind_direction": weather_data.get(
                        "wind_direction"
                    ),

                    "visibility": weather_data.get(
                        "visibility"
                    ),

                    "precipitation": weather_data.get(
                        "precipitation"
                    ),

                    "condition":
                        weather_condition_from_code(
                            weather_code
                        ),

                    "lightning":
                        is_thunderstorm(
                            weather_code
                        )
                }

                print(
                    f"[WEATHER BATCH] SUCCESS "
                    f"{node['node_id']} -> "
                    f"{results[key]}"
                )

            # -------------------------------------------------
            # Delay between batches
            # -------------------------------------------------

            if (
                start + BATCH_SIZE
                < len(unique_nodes)
            ):

                await asyncio.sleep(
                    BATCH_DELAY
                )

    # -----------------------------------------------------
    # Map results back to ALL original nodes
    # -----------------------------------------------------

    final_results = {}

    for node in nodes:

        key = coordinate_key(node)

        final_results[
            node["node_id"]
        ] = results.get(
            key,
            {}
        )

    print(
        f"[WEATHER BATCH] Completed "
        f"{sum(bool(v) for v in final_results.values())}/"
        f"{len(final_results)}"
    )

    return final_results