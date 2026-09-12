import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from services.marine_data_sources import (
    get_pfz_candidates
)


# ---------------------------------------------------------
# Test 1: Without radius
# ---------------------------------------------------------

print("\n========== TEST 1: WITHOUT RADIUS ==========\n")

result = get_pfz_candidates(
    latitude=13.08,
    longitude=80.27
)

print("Number of PFZ zones:")
print(result["count"])

print("\nPFZ zones:")

for pfz_id, pfz in result["pfz_zones"].items():
    print(pfz_id, ":", pfz)


# ---------------------------------------------------------
# Test 2: With radius
# ---------------------------------------------------------

print("\n========== TEST 2: WITH RADIUS ==========\n")

result_radius = get_pfz_candidates(
    latitude=13.08,
    longitude=80.27,
    radius_km=50
)

print("Radius:")
print(result_radius["radius_km"], "km")

print("\nNumber of PFZ zones:")
print(result_radius["count"])

print("\nPFZ zones:")

for pfz_id, pfz in result_radius["pfz_zones"].items():
    print(pfz_id, ":", pfz)


print("\n============================================")