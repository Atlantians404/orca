from .schema import RiskInput


def validate_risk_input(data: dict) -> RiskInput:

    try:

        return RiskInput.model_validate(data)

    except Exception as e:

        raise ValueError(
            f"Invalid risk input: {e}"
        ) from e