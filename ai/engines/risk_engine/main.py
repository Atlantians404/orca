from .validator import validate_agent_data
from .scoring import calculate_risk

def format_time(timestamp: str) -> str:
    if " " in timestamp:
        return timestamp.split(" ")[-1]
    return timestamp

def calculate_all_results(agent_data):
    results = []
    for pfz_name, time_data in agent_data.items():
        for timestamp, risk_input in time_data.items():
            risk = calculate_risk(risk_input)
            results.append({
                "pfz_name": pfz_name,
                "time": format_time(timestamp),
                "risk_score": risk["risk_score"],
                "risk_level": risk["risk_level"]
            })
    return results

def rank_results(results):
    """
    Lower score = safer.

    Therefore:
        lowest score → highest score
    """
    return sorted(
        results,
        key=lambda item: item["risk_score"]
    )

def rank_pfz_by_average(results):
    """
    Used for Case 3.

    Each PFZ has multiple time-based
    risk scores.

    The average risk score is used
    to rank the PFZs.

    Lower average score = safer PFZ.
    """
    pfz_scores = {}

    for result in results:
        pfz_name = result["pfz_name"]

        if pfz_name not in pfz_scores:
            pfz_scores[pfz_name] = []

        pfz_scores[pfz_name].append(
            result["risk_score"]
        )

    pfz_average = []

    for pfz_name, scores in pfz_scores.items():
        average_score = sum(scores) / len(scores)

        pfz_average.append({
            "pfz_name": pfz_name,
            "average_score": average_score
        })

    return sorted(
        pfz_average,
        key=lambda item: item["average_score"]
    )

def format_case3_output(results, top_pfz):
    """
    Return all requested time results
    for the selected Top 5 PFZs.
    """
    output = []

    for pfz in top_pfz:
        pfz_name = pfz["pfz_name"]
        time_results = []

        for result in results:
            if result["pfz_name"] == pfz_name:
                time_results.append({
                    "time": result["time"],
                    "risk_score": result["risk_score"],
                    "risk_level": result["risk_level"]
                })

        output.append({
            "pfz_name": pfz_name,
            "times": time_results
        })

    return output

def run_risk_engine(data):
    """
    Handles all four cases.

    Case 1:
        1 PFZ + 1 time
        → 1 result

    Case 2:
        1 PFZ + multiple times
        → all times ranked

    Case 3:
        multiple PFZs + multiple times
        → Top 5 PFZs
        → each PFZ contains all requested times

    Case 4:
        multiple PFZs + 1 time
        → Top 5 PFZs
    """

    validated_data = validate_agent_data(data)

    results = calculate_all_results(
        validated_data
    )

    if not results:
        return {
            "ranked_results": []
        }

    number_of_pfz = len(validated_data)
    number_of_results = len(results)

    if (
        number_of_pfz == 1
        and number_of_results == 1
    ):
        return {
            "ranked_results": results
        }

    if number_of_pfz == 1:
        ranked_results = rank_results(results)

        return {
            "ranked_results": ranked_results
        }

    if number_of_results > number_of_pfz:
        pfz_ranking = rank_pfz_by_average(
            results
        )

        top_pfz = pfz_ranking[:5]

        case3_results = format_case3_output(
            results,
            top_pfz
        )

        return {
            "ranked_results": case3_results
        }

    ranked_results = rank_results(results)
    ranked_results = ranked_results[:5]

    return {
        "ranked_results": ranked_results
    }