import asyncio
import json

import httpx

from services.risk_engine_service.location_service import (
    get_locations_batch
)


MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"

INCOIS_API_URL = (
    "https://sarat.incois.gov.in/"
    "incoismobileappdata/rest/incois/hwassalatestdata"
)



BATCH_SIZE = 50

MAX_CONCURRENT_REQUESTS = 1

MAX_RETRIES = 6

BATCH_DELAY = 3

def normalize(value):

    if value is None:
        return ""

    value = str(value).strip().upper()

    suffixes = [
        " MUNICIPAL CORPORATION",
        " MUNICIPALITY",
        " CORPORATION",
        " CITY CORPORATION"
    ]

    for suffix in suffixes:

        if value.endswith(suffix):

            value = value[
                :-len(suffix)
            ].strip()

            break

    return " ".join(value.split())



def parse_json_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):

        try:

            parsed = json.loads(value)

            if isinstance(parsed, list):
                return parsed

            if isinstance(parsed, dict):
                return [parsed]

        except json.JSONDecodeError:

            return []

    return []


def find_warning(location, alerts):

    district = normalize(
        location.get("district")
    )

    state = normalize(
        location.get("state")
    )

    if not district or not state:
        return None

    for alert in alerts:

        alert_state = normalize(
            alert.get("STATE")
        )

        if alert_state != state:
            continue

        districts = [
            normalize(district_name)
            for district_name in str(
                alert.get("District", "")
            ).split(",")
        ]

        if district in districts:

            return alert

    return None

def coordinate_key(node):

    return (
        round(float(node["latitude"]), 4),
        round(float(node["longitude"]), 4)
    )


# -------------------------------------------------
# FETCH ONE MARINE BATCH
# -------------------------------------------------

async def fetch_marine_batch(
    client,
    batch,
    time,
    semaphore
):

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
            "wave_height",
            "wave_direction",
            "wave_period",
            "swell_wave_height",
            "swell_wave_direction",
            "swell_wave_period",
            "ocean_current_velocity",
            "ocean_current_direction",
            "sea_surface_temperature",
            "sea_level_height_msl"
        ]),

        "timezone": "auto",

        "forecast_hours": 1,

        "cell_selection": "sea"
    }

    async with semaphore:

        for attempt in range(MAX_RETRIES):

            try:

                response = await client.get(
                    MARINE_URL,
                    params=params
                )

                # ---------------------------------
                # RATE LIMIT
                # ---------------------------------

                if response.status_code == 429:

                    if attempt == MAX_RETRIES - 1:

                        response.raise_for_status()

                    retry_after = response.headers.get(
                        "Retry-After"
                    )

                    if retry_after:

                        wait_time = float(
                            retry_after
                        )

                    else:

                        wait_time = min(
                            5 * (2 ** attempt),
                            60
                        )

                    await asyncio.sleep(
                        wait_time
                    )

                    continue


                response.raise_for_status()


                data = response.json()

                if isinstance(data, dict):

                    data = [data]

                return data

            except httpx.RequestError:

                if attempt == MAX_RETRIES - 1:

                    raise

                wait_time = min(
                    5 * (2 ** attempt),
                    60
                )

                await asyncio.sleep(
                    wait_time
                )

    raise RuntimeError(
        "Marine API failed after retries"
    )




async def get_marine_batch(nodes, time):

    if not nodes:
        return {}


    locations = await get_locations_batch(
        nodes
    )

    results = {}

    unique_nodes = {}

    for node in nodes:

        key = coordinate_key(node)

        if key not in unique_nodes:

            unique_nodes[key] = node

    unique_nodes = list(
        unique_nodes.values()
    )

 

    batches = [

        unique_nodes[
            start:start + BATCH_SIZE
        ]

        for start in range(
            0,
            len(unique_nodes),
            BATCH_SIZE
        )
    ]

   

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_REQUESTS
    )

    marine_data = {}

    
    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        for batch_number, batch in enumerate(
            batches
        ):

            data = await fetch_marine_batch(
                client,
                batch,
                time,
                semaphore
            )

            for index, node in enumerate(batch):

                if index >= len(data):

                    continue

                marine_data[
                    coordinate_key(node)
                ] = data[index]


            if batch_number < len(batches) - 1:

                await asyncio.sleep(
                    BATCH_DELAY
                )

        for node in nodes:

            node_id = node["node_id"]

            marine = marine_data.get(
                coordinate_key(node),
                {}
            )

            hourly = marine.get(
                "hourly",
                {}
            )

            location = locations.get(
                node_id,
                {}
            )

            results[node_id] = {

                "latitude":
                    node["latitude"],

                "longitude":
                    node["longitude"],

                "district":
                    location.get(
                        "district"
                    ),

                "state":
                    location.get(
                        "state"
                    ),

                "wave_height":
                    hourly.get(
                        "wave_height",
                        [None]
                    )[0],

                "wave_direction":
                    hourly.get(
                        "wave_direction",
                        [None]
                    )[0],

                "wave_period":
                    hourly.get(
                        "wave_period",
                        [None]
                    )[0],

                "swell_wave_height":
                    hourly.get(
                        "swell_wave_height",
                        [None]
                    )[0],

                "swell_wave_direction":
                    hourly.get(
                        "swell_wave_direction",
                        [None]
                    )[0],

                "swell_wave_period":
                    hourly.get(
                        "swell_wave_period",
                        [None]
                    )[0],

                "ocean_current_velocity":
                    hourly.get(
                        "ocean_current_velocity",
                        [None]
                    )[0],

                "ocean_current_direction":
                    hourly.get(
                        "ocean_current_direction",
                        [None]
                    )[0],

                "sea_surface_temperature":
                    hourly.get(
                        "sea_surface_temperature",
                        [None]
                    )[0],

                "sea_level_height_msl":
                    hourly.get(
                        "sea_level_height_msl",
                        [None]
                    )[0]
            }

        response = await client.get(
            INCOIS_API_URL
        )

        response.raise_for_status()

        incois_data = response.json()

        hwa_list = parse_json_list(
            incois_data.get(
                "HWAJson"
            )
        )

        ssa_list = parse_json_list(
            incois_data.get(
                "SSAJson"
            )
        )

        for node in nodes:

            node_id = node["node_id"]

            location = locations.get(
                node_id,
                {}
            )


            high_wave_warning = find_warning(
                location,
                hwa_list
            )


            swell_surge_warning = find_warning(
                location,
                ssa_list
            )

            alerts = [
                high_wave_warning,
                swell_surge_warning
            ]

            alert_text = " ".join(
                str(alert).lower()
                for alert in alerts
                if alert
            )


            if "severe" in alert_text:

                warning_level = "severe"

            elif "warning" in alert_text:

                warning_level = "warning"

            elif "advisory" in alert_text:

                warning_level = "advisory"

            else:

                warning_level = "None"

            # -------------------------------------
            # ONLY ONE WARNING FIELD
            # -------------------------------------

            results[node_id][
                "warning"
            ] = warning_level

    return results