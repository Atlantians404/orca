from ai.agent_state import AgentState

from ai.tools.geo_tools import (
    protected_zone_tool,
    restricted_zone_tool,
)

from services.risk_engine_service.marine_batch import (
    get_marine_batch
)

from services.risk_engine_service.weather_batch import (
    get_weather_data_batch
)


def format_data(
    pfz,
    marine_data,
    weather_data,
    geo_data
):
    return {
        "marine": {
            "wave_height": marine_data.get(
                "wave_height"
            ),
            "wave_period": marine_data.get(
                "wave_period"
            ),
            "wave_direction": marine_data.get(
                "wave_direction"
            ),
            "swell_wave_height": marine_data.get(
                "swell_wave_height"
            ),
            "swell_wave_period": marine_data.get(
                "swell_wave_period"
            ),
            "swell_wave_direction": marine_data.get(
                "swell_wave_direction"
            ),
            "ocean_current_velocity": marine_data.get(
                "ocean_current_velocity"
            ),
            "ocean_current_direction": marine_data.get(
                "ocean_current_direction"
            ),
            "sea_surface_temperature": marine_data.get(
                "sea_surface_temperature"
            ),
            "sea_level_height_msl": marine_data.get(
                "sea_level_height_msl"
            ),
            "marine_warning": (
                marine_data.get("high_wave_warning")
                or marine_data.get("swell_surge_warning")
                or "None"
            )
        },
        "weather": {
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
            "lightning": weather_data.get(
                "lightning"
            ),
            "condition": weather_data.get(
                "condition"
            )
        },
        "geo": {
            "latitude": pfz.get(
                "latitude"
            ),
            "longitude": pfz.get(
                "longitude"
            ),
            "restricted_area": geo_data.get(
                "restricted_area"
            ),
            "protected_area": geo_data.get(
                "protected_area"
            )
        }
    }


async def collect_geo(pfz):
    latitude = pfz.get(
        "latitude"
    )

    longitude = pfz.get(
        "longitude"
    )

    restricted_area = await restricted_zone_tool.ainvoke({
        "latitude": latitude,
        "longitude": longitude
    })

    protected_area = await protected_zone_tool.ainvoke({
        "latitude": latitude,
        "longitude": longitude
    })

    return {
        "restricted_area": restricted_area,
        "protected_area": protected_area
    }


async def data_collection_engine(
    state: AgentState
) -> AgentState:

    print("\n========== DATA COLLECTION DEBUG ==========")

    pfzs = state.get(
        "pfz_candidates",
        []
    )

    time_context = state.get(
        "time_context"
    )

    print("PFZ count:", len(pfzs) if pfzs else 0)
    print("Time context:", time_context)

    if (
        not pfzs
        or not time_context
        or not time_context.slots
    ):
        print("❌ Missing PFZs or time context")
        return {
            **state,
            "agent_data": {}
        }

    nodes = []
    pfz_map = {}

    for index, pfz in enumerate(pfzs):

        print(f"\nPFZ {index + 1}:")
        print("PFZ:", pfz)

        latitude = pfz.get(
            "latitude"
        )

        longitude = pfz.get(
            "longitude"
        )

        print("latitude:", latitude)
        print("longitude:", longitude)

        if latitude is None or longitude is None:
            print("❌ Missing coordinates")
            continue

        node_id = pfz.get(
            "name",
            f"PFZ_{index + 1:03d}"
        )

        nodes.append({
            "node_id": node_id,
            "latitude": latitude,
            "longitude": longitude
        })

        pfz_map[node_id] = pfz

    print("\nNodes created:", len(nodes))
    print("Nodes:", nodes)

    if not nodes:
        print("❌ NO NODES CREATED")
        return {
            **state,
            "agent_data": {}
        }

    # -------------------------
    # GEO
    # -------------------------

    geo_results = {}

    for node in nodes:

        node_id = node["node_id"]

        print(
            f"\n🌍 Collecting GEO data for {node_id}"
        )

        try:
            geo_results[node_id] = await collect_geo(
                node
            )

            print(
                f"✅ GEO result for {node_id}:",
                geo_results[node_id]
            )

        except Exception as exc:
            print(
                f"❌ GEO failed for {node_id}:",
                repr(exc)
            )

            raise

    # -------------------------
    # DATA COLLECTION
    # -------------------------

    agent_data = {}

    for slot in time_context.slots:

        request_time = (
            f"{slot.date}T"
            f"{slot.start_time}:00"
        )

        output_time = (
            f"{slot.date} "
            f"{slot.start_time}"
        )

        print("\n================================")
        print("REQUEST TIME:", request_time)
        print("OUTPUT TIME:", output_time)
        print("================================")

        # -------------------------
        # MARINE
        # -------------------------

        print("\n🌊 Calling marine batch...")

        try:
            marine_results = await get_marine_batch(
                nodes,
                request_time
            )

            print(
                "✅ Marine result count:",
                len(marine_results)
            )

            print(
                "Marine results:",
                marine_results
            )

        except Exception as exc:
            print(
                "❌ Marine batch failed:",
                repr(exc)
            )
            raise

        # -------------------------
        # WEATHER
        # -------------------------

        print("\n🌤️ Calling weather batch...")

        try:
            weather_results = await get_weather_data_batch(
                nodes,
                request_time
            )

            print(
                "✅ Weather result count:",
                len(weather_results)
            )

            print(
                "Weather results:",
                weather_results
            )

        except Exception as exc:
            print(
                "❌ Weather batch failed:",
                repr(exc)
            )
            raise

        # -------------------------
        # BUILD AGENT DATA
        # -------------------------

        for node in nodes:

            node_id = node["node_id"]

            marine_data = marine_results.get(
                node_id,
                {}
            )

            weather_data = weather_results.get(
                node_id,
                {}
            )

            geo_data = geo_results.get(
                node_id,
                {}
            )

            pfz = pfz_map[node_id]

            result = format_data(
                pfz,
                marine_data,
                weather_data,
                geo_data
            )

            agent_data.setdefault(
                node_id,
                {}
            )[output_time] = result

    print("\n========== DATA COLLECTION RESULT ==========")
    print("agent_data count:", len(agent_data))
    print("agent_data keys:", list(agent_data.keys()))

    return {
        **state,
        "agent_data": agent_data
    }