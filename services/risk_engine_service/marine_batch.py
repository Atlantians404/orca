import asyncio
import json

import httpx

from services.risk_engine_service.location_cache import (
    get_locations_batch
)


MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"

INCOIS_API_URL = (
    "https://sarat.incois.gov.in/"
    "incoismobileappdata/rest/incois/hwassalatestdata"
)

# Number of coordinates in one Open-Meteo request
BATCH_SIZE = 100

# Keep this LOW to avoid 429
MAX_CONCURRENT_REQUESTS = 2

# Retry only when necessary
MAX_RETRIES = 4

# Small pause between successful batches
BATCH_DELAY = 1


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
            value = value[:-len(suffix)].strip()
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


async def fetch_marine_batch(
    client,
    batch,
    time,
    semaphore
):
    """
    Fetch marine data for one batch.

    Uses:
    - one API request for the whole batch
    - limited concurrency
    - retry for 429
    - retry for temporary network errors
    """

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

        # Only need one hour
        "forecast_hours": 1,

        # Only marine grid cells
        "cell_selection": "sea"
    }

    async with semaphore:

        for attempt in range(MAX_RETRIES):

            try:

                response = await client.get(
                    MARINE_URL,
                    params=params
                )

                # -----------------------------
                # RATE LIMIT
                # -----------------------------

                if response.status_code == 429:

                    if attempt == MAX_RETRIES - 1:
                        response.raise_for_status()

                    wait_time = 2 ** attempt

                    print(
                        f"⚠️ Marine API rate limited. "
                        f"Retrying in {wait_time}s..."
                    )

                    await asyncio.sleep(
                        wait_time
                    )

                    continue

                # -----------------------------
                # OTHER HTTP ERRORS
                # -----------------------------

                response.raise_for_status()

                data = response.json()

                if isinstance(data, dict):
                    data = [data]

                return data

            except httpx.RequestError as error:

                if attempt == MAX_RETRIES - 1:
                    raise error

                wait_time = 2 ** attempt

                print(
                    f"⚠️ Marine API request failed. "
                    f"Retrying in {wait_time}s..."
                )

                await asyncio.sleep(
                    wait_time
                )

    return []


async def get_marine_batch(nodes, time):

    # =============================================
    # 1. GET DISTRICT / STATE FROM MONGODB
    # =============================================

    locations = await get_locations_batch(nodes)

    results = {}

    # =============================================
    # 2. CREATE BATCHES
    # =============================================

    batches = [
        nodes[start:start + BATCH_SIZE]
        for start in range(
            0,
            len(nodes),
            BATCH_SIZE
        )
    ]

    print(
        f"🌊 Processing {len(nodes)} nodes "
        f"in {len(batches)} marine batches..."
    )

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_REQUESTS
    )

    # =============================================
    # 3. FETCH MARINE DATA
    # =============================================

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        batch_results = []

        for batch_number, batch in enumerate(
            batches,
            start=1
        ):

            print(
                f"🌊 Marine batch "
                f"{batch_number}/{len(batches)} "
                f"({len(batch)} nodes)"
            )

            data = await fetch_marine_batch(
                client,
                batch,
                time,
                semaphore
            )

            batch_results.append(data)

            # Give API a small breathing gap
            if batch_number < len(batches):
                await asyncio.sleep(
                    BATCH_DELAY
                )

        # =========================================
        # 4. PROCESS MARINE RESULTS
        # =========================================

        for batch, data in zip(
            batches,
            batch_results
        ):

            for index, node in enumerate(batch):

                node_id = node["node_id"]

                marine = (
                    data[index]
                    if index < len(data)
                    else {}
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
                        location.get("district"),

                    "state":
                        location.get("state"),

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

        # =============================================
        # 5. FETCH INCOIS ONLY ONCE
        # =============================================

        print("⚠️ Fetching INCOIS warnings...")

        response = await client.get(
            INCOIS_API_URL
        )

        response.raise_for_status()

        incois_data = response.json()

        hwa_list = parse_json_list(
            incois_data.get("HWAJson")
        )

        ssa_list = parse_json_list(
            incois_data.get("SSAJson")
        )

        # =============================================
        # 6. MATCH INCOIS WARNINGS LOCALLY
        # =============================================

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

            results[node_id][
                "high_wave_warning"
            ] = high_wave_warning

            results[node_id][
                "swell_surge_warning"
            ] = swell_surge_warning

            results[node_id][
                "warning"
            ] = bool(
                high_wave_warning
                or swell_surge_warning
            )

    print(
        f"✅ Marine processing completed "
        f"for {len(results)} nodes."
    )

    return results