from pydantic import ValidationError

from .schemas import RiskInput


def validate_risk_input(data: dict) -> RiskInput:
    """
    Validate incoming data and convert it into a RiskInput object.

    Raises:
        ValueError: If the input does not satisfy the RiskInput schema.
    """

    try:
        return RiskInput.model_validate(data)

    except ValidationError as exc:
        raise ValueError(
            f"Invalid risk input: {exc}"
        ) from exc