from pydantic import ValidationError

from .schema import AgentData, RiskInput


def validate_risk_input(data):

    """
    Validate a single PFZ/time record.
    """

    try:

        return RiskInput.model_validate(data)

    except ValidationError as e:

        raise ValueError(
            f"Invalid risk input: {e}"
        ) from e


def validate_agent_data(data):

    """
    Validate complete agent_data.

    Structure:

    {
        "PFZ01": {
            "2026-08-31 17:00": {
                "request": {...},
                "marine": {...},
                "weather": {...},
                "geo": {...}
            }
        }
    }
    """

    try:

        validated = AgentData.model_validate(
            {"root": data}
        )

        return validated.root

    except ValidationError as e:

        raise ValueError(
            f"Invalid agent data: {e}"
        ) from e