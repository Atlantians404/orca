import httpx


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


async def get_coordinates(place: str) -> dict:

    if not place or not place.strip():
        raise ValueError("Place name cannot be empty.")

    params = {
        "q": place,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }

    headers = {
        "User-Agent": "ORCA-Marine-Risk-System/1.0"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            NOMINATIM_URL,
            params=params,
            headers=headers
        )

    response.raise_for_status()

    data = response.json()

    if not data:
        return {
            "latitude": None,
            "longitude": None,
            "display_name": None
        }

    location = data[0]

    return {
        "latitude": float(location["lat"]),
        "longitude": float(location["lon"]),
        "display_name": location.get("display_name")
    }