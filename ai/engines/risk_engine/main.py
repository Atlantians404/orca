from .engine import RiskEngine
from .validator import validate_risk_input


def run_risk_engine(data: dict):
    """
    Main entry point for the Risk Engine.

    Receives input data, validates it,
    and passes it to the deterministic Risk Engine.
    """

    validated_input = validate_risk_input(data)

    engine = RiskEngine()

    return engine.calculate(validated_input)