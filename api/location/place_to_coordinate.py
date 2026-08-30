import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def get_coordinates(place: str) -> dict:
    """
    Convert a place name into geographic coordinates.

    Parameters:
        place (str): Place name, city, district, landmark, etc.

    Returns:
        dict: Location information containing latitude,
              longitude and display name.
    """

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

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=headers,
        timeout=10
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
print(get_coordinates("Chennai"))