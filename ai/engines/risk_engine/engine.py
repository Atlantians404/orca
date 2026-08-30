from .scoring import (
    score_weather,
    score_marine,
    score_geography,
    calculate_final_risk_score
)


class RiskEngine:

    def process(self, data):

        weather_scores = score_weather(
            data.weather.model_dump()
        )

        marine_scores = score_marine(
            data.marine.model_dump()
        )

        geo_scores = score_geography(
            data.geo.model_dump()
        )

        risk_result = calculate_final_risk_score(
            weather_scores,
            marine_scores,
            geo_scores
        )

        return {
            "weather": weather_scores,
            "marine": marine_scores,
            "geo": geo_scores,
            "risk": risk_result
        }