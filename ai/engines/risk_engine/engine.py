from .scoring import score_weather


class RiskEngine:
    """
    ORCA Risk Engine.

    Current responsibility:
        - Receive validated provider data
        - Calculate individual risk-factor scores
        - Return derived risk information only

    Overall risk aggregation will be implemented later.
    """

    def process(self, data: dict) -> dict:
        """
        Process validated ORCA input.

        Returns only the calculated risk information.
        """

        result = {
            "request_id": data["request"]["request_id"]
        }

        # -------------------------------------------------
        # WEATHER
        # -------------------------------------------------

        if "weather" in data:
            result["weather"] = score_weather(
                data["weather"]
            )

        return result