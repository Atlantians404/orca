from langchain_core.messages import ToolMessage

from ai.configs.config import llm

from ai.tools.geo_tools import (
    protected_zone_tool,
    restricted_zone_tool,
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
    high_wave_alert_tool,
    high_wave_warning_message_tool,
    high_wave_warning_color_tool,
)

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

from langchain_core.tools import tool

from services.location.place_to_coordinate import (
    get_coordinates,
)

from services.location.pfz_to_coordinate import (
    get_pfz_coordinates,
)


# =========================================================
# LOCATION TOOLS
# =========================================================

@tool
async def coordinates_tool(place: str) -> dict:
    """
    Convert a place name into latitude and longitude coordinates.
    """

    return await get_coordinates(place)


@tool
async def pfz_coordinates_tool(pfz_name: str) -> dict:
    """
    Get the latitude and longitude of a PFZ using its name.
    """

    return await get_pfz_coordinates(pfz_name)


# =========================================================
# GENERAL TOOLS
# =========================================================

GENERAL_TOOLS = [

    # =====================================================
    # LOCATION
    # =====================================================

    coordinates_tool,
    pfz_coordinates_tool,

    # =====================================================
    # WEATHER
    # =====================================================

    temperature_tool,
    wind_speed_tool,
    wind_direction_tool,
    wind_gust_tool,
    visibility_tool,
    precipitation_tool,
    weather_code_tool,
    weather_condition_tool,
    thunderstorm_tool,

    # =====================================================
    # MARINE
    # =====================================================

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

    # =====================================================
    # MARINE WARNINGS
    # =====================================================

    marine_warning_tool,
    high_wave_alert_tool,
    high_wave_warning_message_tool,
    high_wave_warning_color_tool,

    # =====================================================
    # MARINE ZONES
    # =====================================================

    protected_zone_tool,
    restricted_zone_tool,
]


# =========================================================
# TOOL LOOKUP
# =========================================================

TOOL_MAP = {
    tool.name: tool
    for tool in GENERAL_TOOLS
}


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are ORCA's General Marine and Fishing Assistant.

You answer questions about:

- weather
- temperature
- wind
- visibility
- precipitation
- thunderstorms
- waves
- swell
- ocean currents
- sea surface temperature
- sea level
- marine warnings
- protected zones
- restricted zones
- locations
- PFZ locations

RULES:

1. Use a tool whenever actual weather, marine,
   location, or PFZ data is required.

2. Never invent weather or marine values.

3. You may call multiple tools when required.

4. If the user gives a place name instead of coordinates,
   use coordinates_tool first.

5. After coordinates_tool returns coordinates,
   use those coordinates with the appropriate
   weather or marine tool.

6. If the user asks about a specific PFZ by name,
   use pfz_coordinates_tool when coordinates are required.

7. Do not call unnecessary tools.

8. For unrelated questions, answer normally if appropriate.
   Do not call marine tools unnecessarily.

9. After receiving all required tool results,
   provide one clear final answer.

10. Do not expose internal tool calls.
"""


# =========================================================
# BIND TOOLS
# =========================================================

llm_with_tools = llm.bind_tools(
    GENERAL_TOOLS
)


# =========================================================
# GENERAL AGENT
# =========================================================

async def general_agent(messages):

    current_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        *messages,
    ]

    while True:

        # =================================================
        # ASK LLM
        # =================================================

        response = await llm_with_tools.ainvoke(
            current_messages
        )

        current_messages.append(response)

        # =================================================
        # NO TOOL CALL
        # =================================================

        if not response.tool_calls:

            # ---------------------------------------------
            # Valid final response
            # ---------------------------------------------

            if (
                response.content
                and response.content.strip()
            ):
                return {
                    "messages": current_messages
                }

            # ---------------------------------------------
            # Empty response
            # Ask LLM to continue
            # ---------------------------------------------

            current_messages.append({
                "role": "user",
                "content": (
                    "Continue. Check whether any requested "
                    "information is still missing. If information "
                    "is missing, call the required tool. Otherwise "
                    "provide the final answer."
                ),
            })

            continue

        # =================================================
        # TOOL CALLS
        # =================================================

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            tool_args = tool_call["args"]

            tool_call_id = tool_call["id"]

            # ---------------------------------------------
            # Find tool
            # ---------------------------------------------

            selected_tool = TOOL_MAP.get(
                tool_name
            )

            # ---------------------------------------------
            # Tool not found
            # ---------------------------------------------

            if selected_tool is None:

                tool_result = (
                    f"Tool '{tool_name}' is not available."
                )

            # ---------------------------------------------
            # Execute tool
            # ---------------------------------------------

            else:

                try:

                    tool_result = await selected_tool.ainvoke(
                        tool_args
                    )

                except Exception as e:

                    tool_result = (
                        f"Tool execution failed: {str(e)}"
                    )

            # ---------------------------------------------
            # Send result back to LLM
            # ---------------------------------------------

            current_messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call_id,
                )
            )