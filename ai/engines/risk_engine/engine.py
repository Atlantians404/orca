from .schemas import RiskInput, RiskResult


class RiskEngine:
    """
    Deterministic risk engine.

    The engine receives validated risk inputs and produces
    a stable RiskResult.
    """

    def calculate(self, risk_input: RiskInput) -> RiskResult:
        """
        Calculate the overall risk.

        The detailed deterministic scoring rules will be added
        after the input/output pipeline is verified.
        """

        return RiskResult(
            request_id=risk_input.request.request_id,
            score=0.0,
            level="LOW",
            reasons=["Risk calculation rules are not implemented yet."],
            recommendation=None,
            route_required=risk_input.request.requires_route,
        )
if __name__ == "__main__":
    print("Risk Engine module is working.")