import json
from datetime import datetime
from zoneinfo import ZoneInfo

from ai.configs.config import llm
from ai.agent_state import AgentState
from ai.prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from ai.prompts.time_prompt import TIME_PROMPT

from ai.schemas.location import Location
from ai.schemas.time import TimeContext, TimeSlot


TIMEZONE = "Asia/Kolkata"


async def _parse_time_input(
    time_input: str | None,
    current_date: str,
) -> TimeContext | None:

    if not time_input:
        return None

    time_input = time_input.strip()

    if not time_input:
        return None

    # ========================================================
    # TIME EXTRACTION
    # ========================================================

    message = TIME_PROMPT.format(
        current_date=current_date,
        time_input=time_input,
    )

    response = await llm.ainvoke(
        message
    )

    content = response.content.strip()

    # Handle accidental markdown fences
    if content.startswith("```"):

        content = content.replace(
            "```json",
            "",
            1,
        )

        content = content.replace(
            "```",
            "",
            1,
        )

        content = content.strip()

    result = json.loads(
        content
    )

    time_type = result.get(
        "time_type"
    )

    # ========================================================
    # MISSING
    # ========================================================

    if time_type == "missing":
        return None

    # ========================================================
    # SPECIFIC
    # ========================================================

    if time_type == "specific":

        date_expression = result.get(
            "date"
        )

        time = result.get(
            "time"
        )

        if not date_expression or not time:
            return None

        # IMPORTANT:
        # This currently keeps date resolution in the
        # existing time service.
        from services.time.time_parser import (
            build_specific_time,
        )

        time_context = build_specific_time(
            date_expression=date_expression,
            time=time,
        )

        return time_context

    # ========================================================
    # GENERIC
    # ========================================================

    if time_type == "generic":

        date_expression = result.get(
            "date"
        )

        period = result.get(
            "period"
        )

        if not date_expression or not period:
            return None

        from services.time.time_parser import (
            build_generic_time,
        )

        time_context = build_generic_time(
            date_expression=date_expression,
            period=period,
        )

        return time_context

    return None


async def orchestrate(
    state: AgentState,
) -> dict:

    prompt = state["prompt"]

    # ========================================================
    # CURRENT DATE
    # ========================================================

    current_date = datetime.now(
        ZoneInfo(TIMEZONE)
    ).date().isoformat()

    # ========================================================
    # ORCHESTRATOR
    # ========================================================

    message = ORCHESTRATOR_PROMPT.format(
        current_date=current_date,
        prompt=prompt,
    )

    response = await llm.ainvoke(
        message
    )

    content = response.content.strip()

    # Handle accidental markdown fences
    if content.startswith("```"):

        content = content.replace(
            "```json",
            "",
            1,
        )

        content = content.replace(
            "```",
            "",
            1,
        )

        content = content.strip()

    # ========================================================
    # PARSE ORCHESTRATOR JSON
    # ========================================================

    result = json.loads(
        content
    )

    # ========================================================
    # QUERY TYPE
    # ========================================================

    query_type = result.get(
        "query_type",
        "general",
    )

    if query_type not in {
        "general",
        "safety",
        "planning",
    }:
        query_type = "general"

    # ========================================================
    # LOCATION
    # ========================================================

    location = None

    extracted_location = result.get(
        "location"
    )

    if isinstance(
        extracted_location,
        dict,
    ):

        place = extracted_location.get(
            "place"
        )

        latitude = extracted_location.get(
            "latitude"
        )

        longitude = extracted_location.get(
            "longitude"
        )

        if (
            place
            or latitude is not None
            or longitude is not None
        ):

            location = Location(
                place=place,
                latitude=(
                    float(latitude)
                    if latitude is not None
                    else None
                ),
                longitude=(
                    float(longitude)
                    if longitude is not None
                    else None
                ),
            )

    # ========================================================
    # TIME
    # ========================================================

    time_context = None

    time_input = result.get(
        "time_input"
    )

    if time_input:

        try:

            time_context = await _parse_time_input(
                time_input=time_input,
                current_date=current_date,
            )

        except Exception as exc:

            print(
                f"[ORCHESTRATOR] Time parsing failed: {exc}"
            )

            time_context = None

    # ========================================================
    # RETURN STATE
    # ========================================================

    return {
        "query_type": query_type,

        "location": location,

        "time_context": time_context,

        "distance_km": result.get(
            "distance_km"
        ),

        "selected_pfz_name": result.get(
            "selected_pfz_name"
        ),

        "route_required": result.get(
            "route_required",
            False,
        ),

        "workflow_status": "IN_PROGRESS",
    }