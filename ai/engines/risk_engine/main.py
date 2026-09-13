from .validator import validate_agent_data
from .scoring import calculate_risk


def format_time(timestamp: str) -> str:
    """
    Extract the time portion from a timestamp.

    Example:
        2026-09-13 06:00:00
        -> 06:00:00
    """

    if " " in timestamp:
        return timestamp.split(" ")[-1]

    return timestamp


def calculate_all_results(agent_data):
    """
    Calculate risk for every PFZ and every requested time.

    Output:

    [
        {
            "pfz_name": "...",
            "time": "...",
            "risk_score": ...,
            "risk_level": "..."
        }
    ]
    """

    results = []

    for pfz_name, time_data in agent_data.items():

        if not isinstance(time_data, dict):
            continue

        for timestamp, risk_input in time_data.items():

            risk = calculate_risk(risk_input)

            results.append(
                {
                    "pfz_name": pfz_name,
                    "time": format_time(timestamp),
                    "risk_score": risk["risk_score"],
                    "risk_level": risk["risk_level"],
                }
            )

    return results


def rank_results(results):
    """
    Rank individual PFZ/time results.

    Lower risk score = safer.

    Therefore:

        lowest score -> highest score
    """

    return sorted(
        results,
        key=lambda item: item["risk_score"],
    )


def rank_pfz_by_average(results):
    """
    Rank PFZs using their average risk score.

    Used when multiple PFZs have multiple
    requested times.

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

        if not scores:
            continue

        average_score = (
            sum(scores) / len(scores)
        )

        pfz_average.append(
            {
                "pfz_name": pfz_name,
                "average_score": average_score,
            }
        )

    return sorted(
        pfz_average,
        key=lambda item: item["average_score"],
    )


def format_pfz_results(results, pfz_names):
    """
    Convert flat risk results into a consistent
    PFZ-based structure.

    Example input:

    [
        {
            "pfz_name": "Coromandel",
            "time": "06:00",
            "risk_score": 20,
            "risk_level": "LOW"
        }
    ]

    Output:

    [
        {
            "pfz_name": "Coromandel",
            "times": [
                {
                    "time": "06:00",
                    "risk_score": 20,
                    "risk_level": "LOW"
                }
            ]
        }
    ]
    """

    output = []

    for pfz_name in pfz_names:

        time_results = []

        for result in results:

            if result["pfz_name"] != pfz_name:
                continue

            time_results.append(
                {
                    "time": result["time"],
                    "risk_score": result["risk_score"],
                    "risk_level": result["risk_level"],
                }
            )

        output.append(
            {
                "pfz_name": pfz_name,
                "times": time_results,
            }
        )

    return output


def run_risk_engine(data):
    """
    Handles all four cases.

    Case 1:
        1 PFZ + 1 time
        -> 1 PFZ
        -> 1 time result

    Case 2:
        1 PFZ + multiple times
        -> 1 PFZ
        -> all time results

    Case 3:
        multiple PFZs + multiple times
        -> Top 5 PFZs
        -> every PFZ contains all requested times

    Case 4:
        multiple PFZs + 1 time
        -> Top 5 PFZs
        -> each PFZ contains its time result

    IMPORTANT:
        Every case returns the same structure:

        {
            "ranked_results": [
                {
                    "pfz_name": "...",
                    "times": [...]
                }
            ]
        }
    """

    # ---------------------------------------------------------
    # Validate input
    # ---------------------------------------------------------

    validated_data = validate_agent_data(data)

    if not validated_data:
        return {
            "ranked_results": []
        }

    # ---------------------------------------------------------
    # Calculate risk for every PFZ/time combination
    # ---------------------------------------------------------

    results = calculate_all_results(
        validated_data
    )

    if not results:
        return {
            "ranked_results": []
        }

    # ---------------------------------------------------------
    # Determine number of PFZs and results
    # ---------------------------------------------------------

    number_of_pfz = len(validated_data)

    number_of_results = len(results)

    # ---------------------------------------------------------
    # CASE 1
    #
    # 1 PFZ + 1 time
    # ---------------------------------------------------------

    if (
        number_of_pfz == 1
        and number_of_results == 1
    ):

        pfz_names = list(
            validated_data.keys()
        )

        ranked_results = format_pfz_results(
            results,
            pfz_names,
        )

        return {
            "ranked_results": ranked_results
        }

    # ---------------------------------------------------------
    # CASE 2
    #
    # 1 PFZ + multiple times
    # ---------------------------------------------------------

    if number_of_pfz == 1:

        # Rank individual time results.
        ranked_results = rank_results(
            results
        )

        # The PFZ itself is still a single
        # selection option.
        pfz_names = list(
            {
                result["pfz_name"]
                for result in ranked_results
            }
        )

        formatted_results = format_pfz_results(
            ranked_results,
            pfz_names,
        )

        return {
            "ranked_results": formatted_results
        }

    # ---------------------------------------------------------
    # CASE 3
    #
    # Multiple PFZs + multiple times
    # ---------------------------------------------------------

    if number_of_results > number_of_pfz:

        pfz_ranking = rank_pfz_by_average(
            results
        )

        # Top 5 safest PFZs.
        top_pfz = pfz_ranking[:5]

        top_pfz_names = [
            pfz["pfz_name"]
            for pfz in top_pfz
        ]

        formatted_results = format_pfz_results(
            results,
            top_pfz_names,
        )

        return {
            "ranked_results": formatted_results
        }

    # ---------------------------------------------------------
    # CASE 4
    #
    # Multiple PFZs + 1 time
    # ---------------------------------------------------------

    ranked_results = rank_results(
        results
    )

    # Top 5 safest PFZs.
    ranked_results = ranked_results[:5]

    top_pfz_names = [
        result["pfz_name"]
        for result in ranked_results
    ]

    formatted_results = format_pfz_results(
        results,
        top_pfz_names,
    )

    return {
        "ranked_results": formatted_results
    }