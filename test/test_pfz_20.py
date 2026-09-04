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


# User's location
USER_LATITUDE = 13.08
USER_LONGITUDE = 80.27

# Number of PFZs required
NUMBER_OF_ZONES = 20


# Connect to MongoDB
collection = get_mongodb_collection()


# Get existing PFZ advisory for testing
advisory = collection.find_one({
    "forecast_validity.from": "29 Aug 2026",
    "forecast_validity.to": "30 Aug 2026"
})


if not advisory:
    print("PFZ advisory not found.")
    exit()


# IMPORTANT:
# PFZ locations are stored in "pfz_locations"
locations = advisory.get(
    "pfz_locations",
    []
)


candidates = []


# Calculate distance from user's location
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


    distance = calculate_distance_km(
        USER_LATITUDE,
        USER_LONGITUDE,
        pfz_latitude,
        pfz_longitude
    )


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


# Take nearest 20
candidates = candidates[
    :NUMBER_OF_ZONES
]


# Convert to required dictionary format
pfz_zones = {}

for index, pfz in enumerate(
    candidates,
    start=1
):

    pfz_zones[
        f"pfz{index}"
    ] = pfz


# Print result
print("\n========== PFZ RESULT ==========\n")

print("Source location:")
print({
    "latitude": USER_LATITUDE,
    "longitude": USER_LONGITUDE
})

print(
    "\nNumber of PFZ zones:",
    len(pfz_zones)
)

print("\nPFZ zones:\n")

for pfz_id, pfz in pfz_zones.items():

    print(
        pfz_id,
        ":",
        pfz
    )

print("\n================================")