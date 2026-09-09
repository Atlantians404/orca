import asyncio
import httpx

from api.weather.weather import (
    WEATHER_URL,
    get_weather_condition,
    is_thunderstorm
)

BATCH_SIZE = 100
BATCH_DELAY = 2
MAX_RETRIES = 6


def coordinate_key(node):
    return (
        round(float(node["latitude"]), 4),
        round(float(node["longitude"]), 4)
    )


async def get_weather_data_batch(nodes, time):

    if not nodes:
        return {}

    results = {}

    # Remove duplicate coordinates
    unique_nodes = {}

    for node in nodes:
        key = coordinate_key(node)

        if key not in unique_nodes:
            unique_nodes[key] = node

    unique_nodes = list(unique_nodes.values())

    async with httpx.AsyncClient(
        timeout=30,
        limits=httpx.Limits(
            max_connections=1,
            max_keepalive_connections=1
        )
    ) as client:

        for start in range(
            0,
            len(unique_nodes),
            BATCH_SIZE
        ):

            batch = unique_nodes[
                start:start + BATCH_SIZE
            ]

            latitudes = ",".join(
                str(node["latitude"])
                for node in batch
            )

            longitudes = ",".join(
                str(node["longitude"])
                for node in batch
            )

            params = {
                "latitude": latitudes,
                "longitude": longitudes,
                "hourly": ",".join([
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "visibility",
                    "precipitation",
                    "weather_code"
                ]),
                "timezone": "auto",
                "start_hour": time,
                "end_hour": time
            }

            for attempt in range(MAX_RETRIES):

                try:

                    response = await client.get(
                        WEATHER_URL,
                        params=params
                    )

                    if response.status_code == 429:

                        retry_after = response.headers.get(
                            "Retry-After"
                        )

                        if retry_after:
                            wait_time = float(retry_after)
                        else:
                            wait_time = min(
                                5 * (2 ** attempt),
                                60
                            )

                        await asyncio.sleep(wait_time)
                        continue

                    response.raise_for_status()

                    data = response.json()

                    if isinstance(data, dict):
                        data = [data]

                    for index, node in enumerate(batch):

                        if index >= len(data):
                            continue

                        hourly = data[index].get(
                            "hourly",
                            {}
                        )

                        weather_code = hourly.get(
                            "weather_code",
                            [None]
                        )[0]

                        results[
                            coordinate_key(node)
                        ] = {
                            "wind_speed": hourly.get(
                                "wind_speed_10m",
                                [None]
                            )[0],

                            "wind_direction": hourly.get(
                                "wind_direction_10m",
                                [None]
                            )[0],

                            "visibility": hourly.get(
                                "visibility",
                                [None]
                            )[0],

                            "precipitation": hourly.get(
                                "precipitation",
                                [None]
                            )[0],

                            "condition": (
                                get_weather_condition(
                                    weather_code
                                )
                            ),

                            "lightning": (
                                is_thunderstorm(
                                    weather_code
                                )
                            )
                        }

                    break

                except httpx.RequestError:

                    if attempt == MAX_RETRIES - 1:
                        raise

                    await asyncio.sleep(
                        min(5 * (2 ** attempt), 60)
                    )

            else:
                raise RuntimeError(
                    f"Weather API failed after retries "
                    f"for batch {start}"
                )

            # Control request rate
            if start + BATCH_SIZE < len(unique_nodes):
                await asyncio.sleep(BATCH_DELAY)

    # Map results back to ALL original nodes
    final_results = {}

    for node in nodes:

        key = coordinate_key(node)

        final_results[node["node_id"]] = results.get(
            key,
            {}
        )

<<<<<<< HEAD
                    "condition": get_weather_condition(
                        weather_code
                    ),

                    "lightning": is_thunderstorm(
                        weather_code
                    )
                }

    return {
        node["node_id"]: results[node["node_id"]]
        for node in nodes
    }
=======
    return final_results
>>>>>>> origin/main
