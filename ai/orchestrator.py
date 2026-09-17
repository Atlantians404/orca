import json
from datetime import datetime
from zoneinfo import ZoneInfo

from ai.configs.config import llm
from ai.agent_state import AgentState
from ai.prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from ai.prompts.time_prompt import TIME_PROMPT

from ai.schemas.location import Location
from ai.schemas.time import TimeContext


TIMEZONE = "Asia/Kolkata"


def _parse_json_response(content: str) -> dict:
    """
    Safely extract a JSON object from an LLM response.

    Handles:
    - normal JSON
    - ```json ... ```
    - ``` ... ```
    - extra text before/after JSON
    """

    content = content.strip()

    # Remove markdown fences
    if content.startswith("```"):
        lines = content.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    # First try normal JSON
    try:
        result = json.loads(content)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from surrounding text
    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1 and end > start:
        json_content = content[start:end + 1]

        try:
            result = json.loads(json_content)

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    # Log the actual LLM response for debugging
    print("\n========== INVALID LLM JSON ==========")
    print(content)
    print("======================================\n")

    raise ValueError(
        "LLM returned invalid JSON."
    )


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

    result = _parse_json_response(
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

        if not time:
            return None

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

        if not period:
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
    # CONVERSATION SUMMARY
    # ========================================================

    conversation_summary = state.get(
        "conversation_summary",
        ""
    ) or ""

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
        conversation_summary=conversation_summary,
        prompt=prompt,
    )

    response = await llm.ainvoke(
        message
    )

    content = response.content.strip()

    # ========================================================
    # PARSE ORCHESTRATOR JSON
    # ========================================================

    result = _parse_json_response(
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