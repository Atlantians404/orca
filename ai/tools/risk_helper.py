import asyncio
from ai.engines.risk_engine.main import run_risk_engine
from services.risk_engine_service.marine_batch import get_marine_data_batch
from services.risk_engine_service.weather_batch import get_weather_data_batch
from services.location.marine_zones import is_protected, is_restricted

async def get_geo_data_batch(nodes):
    async def process_node(node):
        latitude = node["latitude"]
        longitude = node["longitude"]
        restricted, protected = await asyncio.gather(
            is_restricted(latitude, longitude),
            is_protected(latitude, longitude)
        )
        return node["node_id"], {
            "latitude": latitude,
            "longitude": longitude,
            "restricted_area": restricted,
            "protected_area": protected
        }
    results = await asyncio.gather(
        *(process_node(node) for node in nodes)
    )
    return dict(results)

def build_risk_input(node, time, weather, marine, geo):
    node_id = node["node_id"]
    return {
        "request": {
            "request_id": node_id,
            "requires_route": False,
            "forecast_hours": 24
        },
        "marine": marine[node_id],
        "weather": {
            **weather[node_id],
            "wave_height": marine[node_id]["wave_height"]
        },
        "geo": geo[node_id]
    }

async def evaluate_node(node, time, weather, marine, geo):
    risk_input = build_risk_input(
        node, time, weather, marine, geo
    )
    agent_data = {
        node["node_id"]: {
            time: risk_input
        }
    }
    result = run_risk_engine(agent_data)
    risk_result = result["ranked_results"][0]
    return {
        "node_id": node["node_id"],
        "risk_score": risk_result["risk_score"],
        "safe": risk_result["risk_score"] <= 60
    }

async def process_grid(k7_input):
    nodes = k7_input["nodes"]
    time = k7_input["time"]

    weather, marine, geo = await asyncio.gather(
        get_weather_data_batch(nodes, time),
        get_marine_data_batch(nodes, time),
        get_geo_data_batch(nodes)
    )

    results = await asyncio.gather(
        *(
            evaluate_node(
                node,
                time,
                weather,
                marine,
                geo
            )
            for node in nodes
        )
    )

    return list(results)