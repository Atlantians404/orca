from services.marine_data_sources import get_pfz_candidates

result = get_pfz_candidates(
    latitude=13.08,
    longitude=80.27
)

print("PFZ RESULT")
print("==========")
print("Count:", result["count"])

for pfz in result["pfz_candidates"]:
    print(pfz)