from services.marine_data_sources import get_pfz_candidates


result = get_pfz_candidates(
    latitude=13.08,
    longitude=80.27,
    requested_date="2026-08-30"
)

print("PFZ RESULT")
print("==========")
print("Count:", result["count"])
print("Date:", result.get("requested_date"))
print("Validity:", result.get("forecast_validity"))

for pfz in result["pfz_candidates"]:
    print(pfz)