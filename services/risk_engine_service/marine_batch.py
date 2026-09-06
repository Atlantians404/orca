import asyncio
import httpx

from api.marine.marine import (
    MARINE_URL,
    INCOIS_API_URL,
    parse_json_list,
    get_location,
    find_matching_district,
    normalize
)


async def get_marine_data_batch(nodes, time):

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
                    "wave_height",
                    "wave_period",
                    "wave_direction",
                    "swell_wave_height",
                    "swell_wave_period",
                    "swell_wave_direction",
                    "ocean_current_velocity",
                    "ocean_current_direction",
                    "sea_surface_temperature",
                    "sea_level_height_msl"
                ],
                "timezone": "auto",
                "start_hour": time,
                "end_hour": time,
                "cell_selection": "sea"
            }

            response = await client.get(
                MARINE_URL,
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

                results[node["node_id"]] = {
                    "wave_height": hourly.get(
                        "wave_height",
                        [None]
                    )[0],

                    "wave_period": hourly.get(
                        "wave_period",
                        [None]
                    )[0],

                    "wave_direction": hourly.get(
                        "wave_direction",
                        [None]
                    )[0],

                    "swell_wave_height": hourly.get(
                        "swell_wave_height",
                        [None]
                    )[0],

                    "swell_wave_period": hourly.get(
                        "swell_wave_period",
                        [None]
                    )[0],

                    "swell_wave_direction": hourly.get(
                        "swell_wave_direction",
                        [None]
                    )[0],

                    "ocean_current_velocity": hourly.get(
                        "ocean_current_velocity",
                        [None]
                    )[0],

                    "ocean_current_direction": hourly.get(
                        "ocean_current_direction",
                        [None]
                    )[0],

                    "sea_surface_temperature": hourly.get(
                        "sea_surface_temperature",
                        [None]
                    )[0],

                    "sea_level_height_msl": hourly.get(
                        "sea_level_height_msl",
                        [None]
                    )[0]
                }

    warning_results = await get_marine_warning_batch(
        nodes
    )

    for node in nodes:

        node_id = node["node_id"]

        warning = warning_results.get(
            node_id,
            {}
        )

        if warning.get("high_wave_warning"):
            results[node_id]["marine_warning"] = "HIGH_WAVE"

        elif warning.get("swell_surge_warning"):
            results[node_id]["marine_warning"] = "SWELL_SURGE"

        else:
            results[node_id]["marine_warning"] = "NONE"

    return {
        node["node_id"]: results[node["node_id"]]
        for node in nodes
    }


async def get_marine_warning_batch(nodes):

    if not nodes:
        return {}

    # Fetch INCOIS only once
    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.get(
            INCOIS_API_URL
        )

        response.raise_for_status()

        data = response.json()

    hwa_list = parse_json_list(
        data.get("HWAJson")
    )

    ssa_list = parse_json_list(
        data.get("SSAJson")
    )

    async def process_node(node):

        location = await get_location(
            node["latitude"],
            node["longitude"]
        )

        hwa_district = find_matching_district(
            location,
            hwa_list
        )

        ssa_district = find_matching_district(
            location,
            ssa_list
        )

        high_wave_warning = None

        if hwa_district:

            for alert in hwa_list:

                districts = [
                    normalize(d)
                    for d in str(
                        alert.get("District", "")
                    ).split(",")
                ]

                if (
                    hwa_district in districts
                    and normalize(
                        alert.get("STATE")
                    )
                    == normalize(
                        location.get("state")
                    )
                ):
                    high_wave_warning = alert
                    break

        swell_surge_warning = None

        if ssa_district:

            for alert in ssa_list:

                districts = [
                    normalize(d)
                    for d in str(
                        alert.get("District", "")
                    ).split(",")
                ]

                if (
                    ssa_district in districts
                    and normalize(
                        alert.get("STATE")
                    )
                    == normalize(
                        location.get("state")
                    )
                ):
                    swell_surge_warning = alert
                    break

        return node["node_id"], {
            "high_wave_warning": high_wave_warning,
            "swell_surge_warning": swell_surge_warning
        }

    results = await asyncio.gather(
        *[
            process_node(node)
            for node in nodes
        ]
    )

    return dict(results)

