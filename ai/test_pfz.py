from ai.tools.marine_tools import get_pfz_candidates


result = get_pfz_candidates(
    latitude=13.08,
    longitude=80.27,
    time="2026-08-30T08:00:00Z"
)

print("\nSTATE:")
print(result["state"])

print("\nNUMBER OF PFZ CANDIDATES:")
print(result["count"])

print("\nTOP PFZ CANDIDATES:")

for pfz in result["pfz_candidates"]:
    print(
        pfz["id"],
        "|",
        pfz["coastal_reference"],
        "|",
        pfz["latitude"],
        pfz["longitude"],
        "|",
        pfz["distance_from_source_km"],
        "km"
    )