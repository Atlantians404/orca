import httpx

from api.weather.weather import (
    WEATHER_URL,
    get_weather_condition,
    is_thunderstorm
)


async def get_weather_data_batch(nodes, time):

    if not nodes:
        return {}

    batch_size = 50
    results = {}

    async with httpx.AsyncClient(timeout=30) as client:

        for start in range(0, len(nodes), batch_size):

            batch = nodes[start:start + batch_size]

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
                "hourly": [
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "visibility",
                    "precipitation",
                    "weather_code"
                ],
                "timezone": "auto",
                "start_hour": time,
                "end_hour": time
            }

            response = await client.get(
                WEATHER_URL,
                params=params
            )

            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict):
                data = [data]

            for index, node in enumerate(batch):

                hourly = data[index].get(
                    "hourly",
                    {}
                )

                weather_code = hourly.get(
                    "weather_code",
                    [None]
                )[0]

                results[node["node_id"]] = {
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