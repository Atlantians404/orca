import httpx

from services.risk_engine_service.location_cache import get_locations_batch


MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"

INCOIS_API_URL = (
    "https://sarat.incois.gov.in/"
    "incoismobileappdata/rest/incois/hwassalatestdata"
)


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
            import json

            parsed = json.loads(value)

            if isinstance(parsed, list):
                return parsed

            if isinstance(parsed, dict):
                return [parsed]

        except json.JSONDecodeError:
            return []

    return []


def find_matching_warning(location, alerts):
    district = normalize(location.get("district"))
    state = normalize(location.get("state"))

    if not district or not state:
        return None

    for alert in alerts:

        if normalize(alert.get("STATE")) != state:
            continue

        districts = [
            normalize(d)
            for d in str(alert.get("District", "")).split(",")
        ]

        if district in districts:
            return alert

    return None


async def get_marine_batch(nodes, time):
    locations = await get_locations_batch(nodes)

    all_results = {}

    async with httpx.AsyncClient(timeout=30) as client:

        # -------------------------------------------------
        # MARINE DATA
        # -------------------------------------------------

        for start in range(0, len(nodes), 50):

            batch = nodes[start:start + 50]

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
                    "wave_direction",
                    "wave_period",
                    "swell_wave_height",
                    "swell_wave_direction",
                    "swell_wave_period",
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

            # Open-Meteo returns one object per coordinate
            if isinstance(data, dict):
                data = [data]

            for index, node in enumerate(batch):

                marine = data[index] if index < len(data) else {}

                hourly = marine.get("hourly", {})

                location = locations.get(
                    node["node_id"],
                    {}
                )

                high_wave_warning = None
                swell_surge_warning = None

                all_results[node["node_id"]] = {
                    "wave_height": hourly.get(
                        "wave_height", [None]
                    )[0],

                    "wave_direction": hourly.get(
                        "wave_direction", [None]
                    )[0],

                    "wave_period": hourly.get(
                        "wave_period", [None]
                    )[0],

                    "swell_wave_height": hourly.get(
                        "swell_wave_height", [None]
                    )[0],

                    "swell_wave_direction": hourly.get(
                        "swell_wave_direction", [None]
                    )[0],

                    "swell_wave_period": hourly.get(
                        "swell_wave_period", [None]
                    )[0],

                    "ocean_current_velocity": hourly.get(
                        "ocean_current_velocity", [None]
                    )[0],

                    "ocean_current_direction": hourly.get(
                        "ocean_current_direction", [None]
                    )[0],

                    "sea_surface_temperature": hourly.get(
                        "sea_surface_temperature", [None]
                    )[0],

                    "sea_level_height_msl": hourly.get(
                        "sea_level_height_msl", [None]
                    )[0],

                    "district": location.get("district"),
                    "state": location.get("state"),

                    "high_wave_warning": high_wave_warning,
                    "swell_surge_warning": swell_surge_warning,

                    "warning": False
                }

        # -------------------------------------------------
        # INCOIS DATA
        # -------------------------------------------------

        response = await client.get(INCOIS_API_URL)

        response.raise_for_status()

        incois_data = response.json()

        hwa_list = parse_json_list(
            incois_data.get("HWAJson")
        )

        ssa_list = parse_json_list(
            incois_data.get("SSAJson")
        )

        # -------------------------------------------------
        # MATCH INCOIS WARNINGS LOCALLY
        # -------------------------------------------------

        for node in nodes:

            node_id = node["node_id"]

            location = locations.get(
                node_id,
                {}
            )

            high_wave_warning = find_matching_warning(
                location,
                hwa_list
            )

            swell_surge_warning = find_matching_warning(
                location,
                ssa_list
            )

            result = all_results[node_id]

            result["high_wave_warning"] = high_wave_warning

            result["swell_surge_warning"] = swell_surge_warning

            result["warning"] = bool(
                high_wave_warning
                or swell_surge_warning
            )

    return all_results