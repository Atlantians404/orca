import asyncio

from ai.engines.risk_engine.main import run_risk_engine

from services.risk_engine_service.weather_batch import (
    get_weather_data_batch,
)
from services.risk_engine_service.marine_batch import (
    get_marine_batch,
)
from services.location.marine_zones import (
    is_protected,
    is_restricted,
)


RISK_MAX_CONCURRENT = 5


async def get_geo_data_batch(nodes):
    async def process_node(node):
        lat = node["latitude"]
        lon = node["longitude"]

        restricted, protected = await asyncio.gather(
            is_restricted(lat, lon),
            is_protected(lat, lon),
        )

        return node["node_id"], {
            "latitude": lat,
            "longitude": lon,
            "restricted_area": restricted,
            "protected_area": protected,
        }

    results = await asyncio.gather(
        *(process_node(node) for node in nodes)
    )

    return dict(results)


def build_risk_input(
    node,
    time,
    weather,
    marine,
    geo,
):
    node_id = node["node_id"]

    marine_data = marine[node_id].copy()

    if "warning" in marine_data:
        marine_data["marine_warning"] = str(
            marine_data.pop("warning")
        )

    return {
        "marine": marine_data,
        "weather": {
            **weather[node_id],
            "wave_height": marine_data["wave_height"],
        },
        "geo": geo[node_id],
    }


async def evaluate_node(
    node,
    time,
    weather,
    marine,
    geo,
    semaphore,
):
    async with semaphore:

        risk_input = build_risk_input(
            node,
            time,
            weather,
            marine,
            geo,
        )

        agent_data = {
            node["node_id"]: {
                time: risk_input,
            }
        }

        result = run_risk_engine(
            agent_data
        )

        ranked_results = result.get(
            "ranked_results",
            [],
        )

        if not ranked_results:
            return {
                "node_id": node["node_id"],
                "risk_score": 100.0,
                "safe": False,
            }

        pfz_result = ranked_results[0]

        # -----------------------------------------------------
        # New risk-engine structure:
        #
        # {
        #     "pfz_name": "...",
        #     "times": [
        #         {
        #             "time": "...",
        #             "risk_score": ...,
        #             "risk_level": ...
        #         }
        #     ]
        # }
        # -----------------------------------------------------

        times = pfz_result.get(
            "times",
            [],
        )

        if not times:
            return {
                "node_id": node["node_id"],
                "risk_score": 100.0,
                "safe": False,
            }

        # Since evaluate_node() sends exactly ONE
        # node + ONE time to run_risk_engine(),
        # there should be exactly one time result.
        risk = times[0]

        risk_score = risk.get(
            "risk_score"
        )

        if risk_score is None:
            return {
                "node_id": node["node_id"],
                "risk_score": 100.0,
                "safe": False,
            }

        return {
            "node_id": node["node_id"],
            "risk_score": risk_score,
            "safe": risk_score <= 60,
        }


async def process_grid(k7_input):
    nodes = k7_input["nodes"]

    time = k7_input["time"]

    weather, marine, geo = await asyncio.gather(
        get_weather_data_batch(
            nodes,
            time,
        ),
        get_marine_batch(
            nodes,
            time,
        ),
        get_geo_data_batch(
            nodes,
        ),
    )

    semaphore = asyncio.Semaphore(
        RISK_MAX_CONCURRENT
    )

    results = await asyncio.gather(
        *(
            evaluate_node(
                node,
                time,
                weather,
                marine,
                geo,
                semaphore,
            )
            for node in nodes
        )
    )

    return list(results)