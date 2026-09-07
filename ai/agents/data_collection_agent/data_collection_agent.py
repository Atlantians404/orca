import json

from ai.agent_state import AgentState
from ai.configs.config import llm

from ai.tools.weather_tools import (
    temperature_tool,
    wind_speed_tool,
    wind_direction_tool,
    wind_gust_tool,
    visibility_tool,
    precipitation_tool,
    weather_code_tool,
    weather_condition_tool,
    thunderstorm_tool,
)

from ai.tools.marine_tools import (
    wave_height_tool,
    wave_direction_tool,
    wave_period_tool,
    swell_wave_height_tool,
    swell_wave_direction_tool,
    swell_wave_period_tool,
    ocean_current_velocity_tool,
    ocean_current_direction_tool,
    sea_surface_temperature_tool,
    sea_level_height_tool,
    marine_warning_tool,
    marine_warning_level_tool,
    high_wave_alert_tool,
    high_wave_warning_message_tool,
    high_wave_warning_color_tool,
)

from ai.tools.geo_tools import (
    protected_zone_tool,
    restricted_zone_tool,
)


# ============================================================
# ALL AVAILABLE DATA TOOLS
# ============================================================

DATA_TOOLS = [
    temperature_tool,
    wind_speed_tool,
    wind_direction_tool,
    wind_gust_tool,
    visibility_tool,
    precipitation_tool,
    weather_code_tool,
    weather_condition_tool,
    thunderstorm_tool,

    wave_height_tool,
    wave_direction_tool,
    wave_period_tool,
    swell_wave_height_tool,
    swell_wave_direction_tool,
    swell_wave_period_tool,
    ocean_current_velocity_tool,
    ocean_current_direction_tool,
    sea_surface_temperature_tool,
    sea_level_height_tool,

    marine_warning_tool,
    marine_warning_level_tool,
    high_wave_alert_tool,
    high_wave_warning_message_tool,
    high_wave_warning_color_tool,

    protected_zone_tool,
    restricted_zone_tool,
]


# ============================================================
# TOOLS REQUIRED FOR DATA COLLECTION
# ============================================================

REQUIRED_DATA_TOOLS = [
    wind_speed_tool,
    wind_direction_tool,
    visibility_tool,
    precipitation_tool,
    weather_condition_tool,
    thunderstorm_tool,

    wave_height_tool,
    wave_period_tool,
    wave_direction_tool,
    swell_wave_height_tool,
    swell_wave_period_tool,
    swell_wave_direction_tool,
    ocean_current_velocity_tool,
    ocean_current_direction_tool,
    sea_surface_temperature_tool,
    sea_level_height_tool,

    marine_warning_level_tool,

    protected_zone_tool,
    restricted_zone_tool,
]


# ============================================================
# TOOL MAP
# ============================================================

tool_map = {
    tool.name: tool
    for tool in REQUIRED_DATA_TOOLS
}

REQUIRED_TOOL_NAMES = [
    tool.name
    for tool in REQUIRED_DATA_TOOLS
]


# ============================================================
# AI TOOL SELECTION
# ============================================================

async def select_required_tools() -> list[str]:
    """
    Ask the AI agent which data collection tools are required.

    The decision is made once for the whole data collection run,
    because the same categories of data are required for every
    PFZ and time slot.
    """

    response = await llm.ainvoke(
        f"""
You are the Data Collection Agent for a marine intelligence system.

Your job is to collect ALL environmental data required for:
- marine conditions
- weather conditions
- geospatial restrictions/protected areas

The following tools are available:

{REQUIRED_TOOL_NAMES}

Select every tool required to collect the complete dataset.

Return ONLY valid JSON in exactly this format:

{{"tools": ["tool_name_1", "tool_name_2"]}}

Rules:
- Use the exact tool names.
- Do not invent tool names.
- Do not add explanations.
- Do not add markdown.
"""
    )

    try:
        decision = json.loads(response.content)

        selected_tools = decision.get("tools", [])

        if not isinstance(selected_tools, list):
            return REQUIRED_TOOL_NAMES.copy()

        # Keep only tools that actually exist.
        selected_tools = [
            tool_name
            for tool_name in selected_tools
            if tool_name in tool_map
        ]

        # If AI returned nothing usable, collect everything.
        if not selected_tools:
            return REQUIRED_TOOL_NAMES.copy()

        return selected_tools

    except Exception:
        # Safe fallback: collect the complete required dataset.
        return REQUIRED_TOOL_NAMES.copy()


# ============================================================
# COLLECT DATA FOR ONE PFZ + ONE TIME
# ============================================================

async def collect_for_pfz_time(
    pfz: dict,
    request_time: str,
    selected_tools: list[str],
) -> dict:
    """
    Collect environmental data for one PFZ and one time slot.
    """

    latitude = pfz.get("latitude")
    longitude = pfz.get("longitude")

    collected = {}

    for tool_name in selected_tools:

        tool = tool_map.get(tool_name)

        if tool is None:
            continue

        # ----------------------------------------------------
        # LOCATION-ONLY TOOLS
        # ----------------------------------------------------

        if tool_name in {
            "marine_warning_level_tool",
            "protected_zone_tool",
            "restricted_zone_tool",
        }:
            args = {
                "latitude": latitude,
                "longitude": longitude,
            }

        # ----------------------------------------------------
        # LOCATION + TIME TOOLS
        # ----------------------------------------------------

        else:
            args = {
                "latitude": latitude,
                "longitude": longitude,
                "time": request_time,
            }

        # ----------------------------------------------------
        # EXECUTE TOOL
        # ----------------------------------------------------

        try:
            result = await tool.ainvoke(args)
            collected[tool_name] = result

        except Exception as e:
            print(
                f"Tool failed: {tool_name} -> {type(e).__name__}: {e}"
            )

            # One external failure must not stop the
            # entire PFZ/time collection.
            collected[tool_name] = None

    # ========================================================
    # FINAL DATA STRUCTURE
    # ========================================================

    return {
        "marine": {
            "wave_height":
                collected.get("wave_height_tool"),

            "wave_period":
                collected.get("wave_period_tool"),

            "wave_direction":
                collected.get("wave_direction_tool"),

            "swell_wave_height":
                collected.get("swell_wave_height_tool"),

            "swell_wave_period":
                collected.get("swell_wave_period_tool"),

            "swell_wave_direction":
                collected.get("swell_wave_direction_tool"),

            "ocean_current_velocity":
                collected.get(
                    "ocean_current_velocity_tool"
                ),

            "ocean_current_direction":
                collected.get(
                    "ocean_current_direction_tool"
                ),

            "sea_surface_temperature":
                collected.get(
                    "sea_surface_temperature_tool"
                ),

            "sea_level_height":
                collected.get(
                    "sea_level_height_tool"
                ),

            "marine_warning":
                collected.get(
                    "marine_warning_level_tool"
                ),
        },

        "weather": {
            "wind_speed":
                collected.get("wind_speed_tool"),

            "wind_direction":
                collected.get(
                    "wind_direction_tool"
                ),

            "wave_height":
                collected.get(
                    "wave_height_tool"
                ),

            "visibility":
                collected.get("visibility_tool"),

            "precipitation":
                collected.get(
                    "precipitation_tool"
                ),

            "lightning":
                collected.get(
                    "thunderstorm_tool"
                ),

            "condition":
                collected.get(
                    "weather_condition_tool"
                ),
        },

        "geo": {
            "latitude": latitude,
            "longitude": longitude,

            "restricted_area":
                collected.get(
                    "restricted_zone_tool"
                ),

            "protected_area":
                collected.get(
                    "protected_zone_tool"
                ),
        },
    }


# ============================================================
# DATA COLLECTION AGENT
# ============================================================

async def data_collection_agent(
    state: AgentState,
) -> AgentState:
    """
    Data Collection Agent.

    Collects marine, weather and geospatial data
    for every PFZ and every requested time slot.
    """

    pfzs = state.get(
        "pfz_candidates",
        []
    )

    time_context = state.get(
        "time_context"
    )

    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    if (
        not pfzs
        or not time_context
        or not time_context.slots
    ):
        return {
            **state,
            "agent_data": {},
        }

    # ========================================================
    # AI SELECTS TOOLS ONCE
    # ========================================================

    selected_tools = await select_required_tools()

    print(
        "\nAI selected tools:",
        selected_tools
    )

    # ========================================================
    # COLLECT DATA
    # ========================================================

    collected_data = {}

    for pfz in pfzs:

        pfz_name = pfz.get(
            "name",
            "unknown"
        )

        latitude = pfz.get(
            "latitude"
        )

        longitude = pfz.get(
            "longitude"
        )

        # Skip invalid PFZs.
        if (
            latitude is None
            or longitude is None
        ):
            continue

        collected_data[pfz_name] = {}

        # ----------------------------------------------------
        # LOOP THROUGH TIME SLOTS
        # ----------------------------------------------------

        for slot in time_context.slots:

            request_time = (
                f"{slot.date}T"
                f"{slot.start_time}:00"
            )

            output_time = (
                f"{slot.date} "
                f"{slot.start_time}"
            )

            collected = await collect_for_pfz_time(
                pfz=pfz,
                request_time=request_time,
                selected_tools=selected_tools,
            )

            collected_data[pfz_name][
                output_time
            ] = collected

    # ========================================================
    # RETURN UPDATED STATE
    # ========================================================

    return {
        **state,
        "agent_data": collected_data,
    }