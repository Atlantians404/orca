from .validator import validate_risk_input
from .engine import RiskEngine


def run_risk_engine(data: dict) -> dict:

    # Validate provider data
    validated_data = validate_risk_input(data)

    # Create engine
    engine = RiskEngine()

    # Process data
    result = engine.process(validated_data)

    # Return risk output
    return result