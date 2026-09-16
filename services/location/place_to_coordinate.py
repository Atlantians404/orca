import asyncio
import time

import httpx


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "ORCA-Marine-Risk-System/1.0"
}

# ---------------------------------------------------------
# Simple in-memory cache
# ---------------------------------------------------------
#
# Key:
#     normalized place name
#
# Value:
#     (timestamp, coordinates)
#
# This prevents repeated Nominatim requests for the
# same location while the Render instance is running.
# ---------------------------------------------------------

_LOCATION_CACHE: dict[str, tuple[float, dict]] = {}

# Keep cached locations for 24 hours.
CACHE_TTL = 60 * 60 * 24


# ---------------------------------------------------------
# Reuse one HTTP client
# ---------------------------------------------------------

_http_client: httpx.AsyncClient | None = None


def _get_cache_key(place: str) -> str:
    """
    Normalize the place name so small differences such as
    extra spaces or capitalization don't create duplicate
    Nominatim requests.
    """

    return " ".join(place.strip().lower().split())


async def _get_http_client() -> httpx.AsyncClient:

    global _http_client

    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=10,
            headers=HEADERS,
        )

    return _http_client


async def get_coordinates(place: str) -> dict:

    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if not place or not place.strip():
        raise ValueError("Place name cannot be empty.")

    cache_key = _get_cache_key(place)

    # -----------------------------------------------------
    # CHECK CACHE
    # -----------------------------------------------------

    cached = _LOCATION_CACHE.get(cache_key)

    if cached is not None:

        cached_time, cached_data = cached

        if time.monotonic() - cached_time < CACHE_TTL:

            print(
                f"[NOMINATIM] Cache hit: {place}"
            )

            return cached_data

        # Cache expired
        del _LOCATION_CACHE[cache_key]

    # -----------------------------------------------------
    # MAKE NOMINATIM REQUEST
    # -----------------------------------------------------

    params = {
        "q": place.strip(),
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }

    client = await _get_http_client()

    print(
        f"[NOMINATIM] Requesting: {place}"
    )

    try:

        response = await client.get(
            NOMINATIM_URL,
            params=params,
        )

        # -------------------------------------------------
        # Rate limited
        # -------------------------------------------------

        if response.status_code == 429:

            print(
                f"[NOMINATIM] 429 rate limit for: {place}"
            )

            # Do NOT retry repeatedly.
            # Returning None coordinates allows the
            # application to continue instead of hanging.
            return {
                "latitude": None,
                "longitude": None,
                "display_name": None,
            }

        response.raise_for_status()

        data = response.json()

    except httpx.HTTPError as exc:

        print(
            f"[NOMINATIM] Request failed for "
            f"{place}: {exc}"
        )

        return {
            "latitude": None,
            "longitude": None,
            "display_name": None,
        }

    # -----------------------------------------------------
    # No location found
    # -----------------------------------------------------

    if not data:

        result = {
            "latitude": None,
            "longitude": None,
            "display_name": None,
        }

        # Cache "not found" too.
        _LOCATION_CACHE[cache_key] = (
            time.monotonic(),
            result,
        )

        return result

    # -----------------------------------------------------
    # Parse location
    # -----------------------------------------------------

    location = data[0]

    result = {
        "latitude": float(location["lat"]),
        "longitude": float(location["lon"]),
        "display_name": location.get("display_name"),
    }

    # -----------------------------------------------------
    # SAVE TO CACHE
    # -----------------------------------------------------

    _LOCATION_CACHE[cache_key] = (
        time.monotonic(),
        result,
    )

    print(
        f"[NOMINATIM] Cached: {place}"
    )

    return result


# ---------------------------------------------------------
# Optional cleanup
# ---------------------------------------------------------

async def close_http_client():
    """
    Call this during application shutdown if desired.
    """

    global _http_client

    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None

