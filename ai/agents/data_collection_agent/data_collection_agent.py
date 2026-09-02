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
from ai.state import AgentState


weather_tools = [
    temperature_tool,
    wind_speed_tool,
    wind_direction_tool,
    wind_gust_tool,
    visibility_tool,
    precipitation_tool,
    weather_code_tool,
    weather_condition_tool,
    thunderstorm_tool,
]

llm_with_tools = llm.bind_tools(weather_tools)


def data_collection_agent(state: AgentState) -> AgentState:
    """
    Collect weather data for the PFZs and time slots
    present in AgentState.
    """

    # Read PFZ information from state
    pfzs = state.get("pfz_candidates", [])

    if not pfzs and state.get("selected_pfz"):
        pfzs = [state["selected_pfz"]]

    # Read time information from state
    time_context = state.get("time_context")

    if not time_context:
        return {
            **state,
            "agent_data": {},
        }

    collected_data = {}

    for pfz in pfzs:

        pfz_id = pfz.get("id") or pfz.get("pfz_id", "unknown")

        latitude = pfz.get("latitude")
        longitude = pfz.get("longitude")

        for slot in time_context.slots:

            time = f"{slot.date}T{slot.start_time}"

            prompt = f"""
            Collect weather data for this PFZ.

            PFZ ID: {pfz_id}
            Latitude: {latitude}
            Longitude: {longitude}
            Time: {time}

            Use the available weather tools to collect:
            temperature,
            wind speed,
            wind direction,
            wind gust,
            visibility,
            precipitation,
            weather code,
            weather condition,
            thunderstorm.
            """

            response = llm_with_tools.invoke(prompt)

            collected_data.setdefault(pfz_id, {})
            collected_data[pfz_id][time] = {
                "llm_response": response,
            }

    return {
        **state,
        "agent_data": collected_data,
    }