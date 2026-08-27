from .engine import RiskEngine
from .validator import validate_risk_input


def run_risk_engine(data: dict) -> dict:
    """
    Main entry point for ORCA Risk Engine.

    Input:
        Clean provider JSON/dictionary

    Processing:
        Validation → Risk Engine → Individual scoring

    Output:
        Risk information as a dictionary
    """

    validated_data = validate_risk_input(data)

    engine = RiskEngine()

    return engine.process(
        validated_data.model_dump()
    )