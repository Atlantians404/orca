import asyncio

from api.weather.weather import (
    get_open_meteo_data,
    weather_condition_from_code,
    is_thunderstorm,
)

WEATHER_CONCURRENCY = 2
WEATHER_DELAY = 0.5

_weather_semaphore = asyncio.Semaphore(WEATHER_CONCURRENCY)


def coordinate_key(node):
    return (
        round(float(node["latitude"]), 4),
        round(float(node["longitude"]), 4),
    )


async def fetch_weather_limited(node, time):
    async with _weather_semaphore:
        await asyncio.sleep(WEATHER_DELAY)

        return await get_open_meteo_data(
            latitude=node["latitude"],
            longitude=node["longitude"],
            weather_time=time,
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

    print(
        f"[WEATHER BATCH] Fetching "
        f"{len(unique_nodes)} coordinates "
        f"(concurrency={WEATHER_CONCURRENCY})"
    )

    tasks = [
        fetch_weather_limited(node, time)
        for node in unique_nodes
    ]

    weather_responses = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    for node, weather_data in zip(unique_nodes, weather_responses):

        key = coordinate_key(node)

        if isinstance(weather_data, Exception):
            print(
                f"[WEATHER BATCH] FAILED "
                f"{node['node_id']} -> {weather_data}"
            )
            results[key] = {}
            continue

        if not weather_data:
            print(
                f"[WEATHER BATCH] EMPTY "
                f"{node['node_id']}"
            )
            results[key] = {}
            continue

        weather_code = weather_data.get("weather_code")

        results[key] = {
            "wind_speed": weather_data.get("wind_speed"),
            "wind_direction": weather_data.get("wind_direction"),
            "visibility": weather_data.get("visibility"),
            "precipitation": weather_data.get("precipitation"),
            "condition": weather_condition_from_code(weather_code),
            "lightning": is_thunderstorm(weather_code),
        }

        print(
            f"[WEATHER BATCH] SUCCESS "
            f"{node['node_id']} -> {results[key]}"
        )

    final_results = {}

    for node in nodes:
        key = coordinate_key(node)
        final_results[node["node_id"]] = results.get(key, {})

    successful = sum(
        bool(value)
        for value in final_results.values()
    )

    print(
        f"[WEATHER BATCH] Completed "
        f"{successful}/{len(final_results)}"
    )

    return final_results