import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from services.marine_data_sources import (
    get_mongodb_collection,
    calculate_distance_km
)


# ---------------------------------------------------------
# User location
# ---------------------------------------------------------

USER_LATITUDE = 13.08
USER_LONGITUDE = 80.27


# ---------------------------------------------------------
# Get MongoDB collection
# ---------------------------------------------------------

collection = get_mongodb_collection()


# ---------------------------------------------------------
# Get historical PFZ advisory for testing
# ---------------------------------------------------------

advisory = collection.find_one({
    "forecast_validity.from": "29 Aug 2026",
    "forecast_validity.to": "30 Aug 2026"
})


if not advisory:
    print("PFZ advisory not found.")
    sys.exit()


# PFZ locations are stored in "pfz_locations"
locations = advisory.get(
    "pfz_locations",
    []
)


# ---------------------------------------------------------
# Function to calculate PFZ candidates
# ---------------------------------------------------------

def test_pfz_candidates(
    latitude,
    longitude,
    radius_km=None,
    number_of_zones=20
):

    candidates = []

    for pfz in locations:

        try:
            pfz_latitude = float(
                pfz["latitude"]
            )

            pfz_longitude = float(
                pfz["longitude"]
            )

        except (KeyError, TypeError, ValueError):
            continue


        # Calculate distance
        distance = calculate_distance_km(
            latitude,
            longitude,
            pfz_latitude,
            pfz_longitude
        )


        # Apply radius if provided
        if (
            radius_km is not None
            and distance > radius_km
        ):
            continue


        candidates.append({
            "name": pfz.get(
                "coastal_reference",
                "Unknown PFZ"
            ),
            "latitude": pfz_latitude,
            "longitude": pfz_longitude,
            "distance_from_source_km": round(
                distance,
                2
            )
        })


    # Sort nearest → farthest
    candidates.sort(
        key=lambda pfz:
        pfz["distance_from_source_km"]
    )


    # Take maximum requested number
    candidates = candidates[
        :number_of_zones
    ]


    # Convert to dictionary
    pfz_zones = {}

    for index, pfz in enumerate(
        candidates,
        start=1
    ):

        pfz_zones[
            f"pfz{index}"
        ] = pfz


    return pfz_zones


# =========================================================
# TEST 1 — No radius
# =========================================================

print(
    "\n========== TEST 1: NO RADIUS ==========\n"
)


result = test_pfz_candidates(
    USER_LATITUDE,
    USER_LONGITUDE
)


print(
    "Number of PFZ zones:",
    len(result)
)


for pfz_id, pfz in result.items():

    print(
        pfz_id,
        ":",
        pfz
    )


# =========================================================
# TEST 2 — Radius = 50 km
# =========================================================

print(
    "\n========== TEST 2: RADIUS = 50 KM ==========\n"
)


result_radius = test_pfz_candidates(
    USER_LATITUDE,
    USER_LONGITUDE,
    radius_km=50
)


print(
    "Radius:",
    50,
    "km"
)


print(
    "Number of PFZ zones:",
    len(result_radius)
)


for pfz_id, pfz in result_radius.items():

    print(
        pfz_id,
        ":",
        pfz
    )


print(
    "\n========================================\n"
)