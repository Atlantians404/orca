import os
import math
from pathlib import Path
from typing import Any
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# MongoDB connection
# ---------------------------------------------------------

def get_mongodb_collection():
    """
    Connect to MongoDB Atlas and return the PFZ collection.
    """

    mongodb_uri = os.getenv("MONGODB_URI")

    if not mongodb_uri:
        raise ValueError(
            "MONGODB_URI not found in .env file."
        )

    client = MongoClient(mongodb_uri)

    db = client["ORCA"]
    collection = db["pfz"]

    return collection


# ---------------------------------------------------------
# Distance calculation
# ---------------------------------------------------------

def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate the distance between two latitude/longitude
    coordinates using the Haversine formula.

    Returns:
        Distance in kilometres.
    """

    earth_radius_km = 6371.0

    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)

    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


# ---------------------------------------------------------
# Get currently valid PFZ advisory
# ---------------------------------------------------------

def get_current_pfz_advisory(collection):
    """
    Find the PFZ advisory that is currently valid.

    Supports advisories with either:
    - both 'from' and 'to' dates
    - only a 'to' date
    """

    today = datetime.now().date()

    advisories = collection.find({})

    for advisory in advisories:

        forecast_validity = advisory.get("forecast_validity", {})

        start_date_text = forecast_validity.get("from")
        end_date_text = forecast_validity.get("to")

        # We need at least an end date.
        if not end_date_text:
            continue

        try:
            end_date = datetime.strptime(
                end_date_text.strip(),
                "%d %b %Y"
            ).date()
        except (ValueError, AttributeError):
            continue

        # If there is a start date, check the complete period.
        if start_date_text:
            try:
                start_date = datetime.strptime(
                    start_date_text.strip(),
                    "%d %b %Y"
                ).date()
            except (ValueError, AttributeError):
                continue

            if start_date <= today <= end_date:
                return advisory

        # If only the end date exists, check whether it has expired.
        else:
            if today <= end_date:
                return advisory

    return None


# ---------------------------------------------------------
# Get nearest PFZ zones
# ---------------------------------------------------------

def get_pfz_candidates(
    latitude: float,
    longitude: float,
    radius_km: float | None = None,
    number_of_zones: int = 20
):
    """
    Find the nearest PFZ zones to a given latitude/longitude.

    Parameters:
        latitude: User/source latitude.
        longitude: User/source longitude.
        radius_km: Optional search radius in kilometres.
        number_of_zones: Maximum number of PFZ zones to return.

    Returns:
        Dictionary containing the nearest PFZ zones.
    """

    # Validate latitude
    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    # Validate longitude
    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    # Validate radius
    if radius_km is not None and radius_km <= 0:
        raise ValueError(
            "Radius must be greater than 0 km."
        )

    # Validate number of zones
    if number_of_zones <= 0:
        raise ValueError(
            "Number of zones must be greater than 0."
        )

    # Get MongoDB collection
    collection = get_mongodb_collection()

    # Get currently valid PFZ advisory
    advisory = get_current_pfz_advisory(collection)

    # No current advisory available
    if not advisory:
        return {
            "state": "pfz_candidates",
            "source_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "radius_km": radius_km,
            "requested_number_of_zones": number_of_zones,
            "returned_number_of_zones": 0,
            "pfz_zones": {},
            "count": 0,
            "message": (
                "No currently valid PFZ advisory is available."
            )
        }

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
            latitude,
            longitude,
            pfz_latitude,
            pfz_longitude
        )

        # If radius is provided,
        # ignore PFZs outside the radius
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

    # Take nearest requested number of zones
    candidates = candidates[
        :number_of_zones
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

    return {
        "state": "pfz_candidates",
        "source_location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "radius_km": radius_km,
        "requested_number_of_zones": number_of_zones,
        "returned_number_of_zones": len(
            pfz_zones
        ),
        "pfz_zones": pfz_zones,
        "count": len(pfz_zones),
        "message": (
            "PFZ candidates retrieved successfully."
            if pfz_zones
            else "No PFZ zones found."
        )
    }


# ---------------------------------------------------------
# Select one PFZ
# ---------------------------------------------------------

def select_pfz(
    pfz_candidates: dict[str, Any],
    pfz_id: str
) -> dict[str, Any] | None:
    """
    Select one PFZ from the returned PFZ dictionary.

    Example:
        select_pfz(result["pfz_zones"], "pfz1")
    """

    if not pfz_candidates:
        return None

    pfz_id = pfz_id.lower().strip()

    return pfz_candidates.get(
        pfz_id
    )

def get_live_pfz_data():
    """
    Retrieve the currently displayed PFZ advisory from the live INCOIS page.

    Uses the existing Edge browser session connected through
    Playwright's remote debugging port.
    """

    from playwright.sync_api import sync_playwright

    INCOIS_URL = "https://www.incois.gov.in/MarineFisheries/TextData?secid=SEC007"

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        pages = browser.contexts[0].pages

        page = None

        for existing_page in pages:
            if "incois.gov.in/MarineFisheries/TextData" in existing_page.url:
                page = existing_page
                break

        if page is None:
            raise RuntimeError(
                "INCOIS Text Data page is not open in the debug Edge browser."
            )

        # Make sure the PFZ data area exists.
        forecast = page.locator("#forecastdata")

        if forecast.count() == 0:
            raise RuntimeError(
                "INCOIS PFZ forecast data was not found on the page."
            )

        # Read the currently displayed PFZ table.
        table_text = forecast.inner_text()

        if not table_text.strip():
            raise RuntimeError(
                "INCOIS PFZ forecast data is empty."
            )

        # Get the page text so we can capture the advisory validity information.
        page_text = page.locator("body").inner_text()

        return {
            "source": "INCOIS",
            "sector": "North Tamil Nadu",
            "advisory_text": page_text,
            "forecast_text": table_text,
        }

def dms_to_decimal(dms_text):
    """
    Convert DMS coordinate text into decimal degrees.

    Example:
    '13 29 40 N' -> 13.494444
    '80 22 46 E' -> 80.379444
    """

    parts = dms_text.split()

    if len(parts) != 4:
        raise ValueError(f"Invalid DMS coordinate: {dms_text}")

    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    direction = parts[3].upper()

    decimal = degrees + (minutes / 60) + (seconds / 3600)

    if direction in ("S", "W"):
        decimal = -decimal

    return round(decimal, 6)


def parse_live_pfz_data(page):
    """
    Parse PFZ rows from the live INCOIS forecast table.
    """

    rows = page.locator("#forecastdata tr")

    pfz_locations = []

    for i in range(1, rows.count()):
        cells = rows.nth(i).locator("td")

        if cells.count() < 7:
            continue

        try:
            coastal_reference = cells.nth(0).inner_text().strip()
            direction = cells.nth(1).inner_text().strip()
            bearing_deg = int(cells.nth(2).inner_text().strip())

            distance_text = cells.nth(3).inner_text().strip()
            depth_text = cells.nth(4).inner_text().strip()

            latitude_text = cells.nth(5).inner_text().strip()
            longitude_text = cells.nth(6).inner_text().strip()

            # Convert distance range: "30-35" -> {"min": 30, "max": 35}
            distance_parts = distance_text.split("-")

            distance_km = {
                "min": int(distance_parts[0]),
                "max": int(distance_parts[1])
            }

            # Convert depth range: "12-17" -> {"min": 12, "max": 17}
            depth_parts = depth_text.split("-")

            depth_m = {
                "min": int(depth_parts[0]),
                "max": int(depth_parts[1])
            }

            # Convert DMS coordinates to decimal degrees
            latitude = dms_to_decimal(latitude_text)
            longitude = dms_to_decimal(longitude_text)

            pfz_locations.append({
                "coastal_reference": coastal_reference,
                "direction": direction,
                "bearing_deg": bearing_deg,
                "distance_km": distance_km,
                "depth_m": depth_m,
                "latitude": latitude,
                "longitude": longitude
            })

        except (ValueError, IndexError):
            # Skip malformed rows instead of stopping the entire retrieval.
            continue

    return pfz_locations

def update_live_pfz_in_mongodb(
    pfz_locations,
    sector="North Tamil Nadu",
    valid_until=None
):
    """
    Save the latest live INCOIS PFZ data into MongoDB.
    """

    collection = get_mongodb_collection()

    # Remove the previous PFZ advisory for this sector
    collection.delete_many({
        "source": "INCOIS",
        "sector": sector
    })

    # Create the new document
    document = {
        "source": "INCOIS",
        "sector": sector,
        "forecast_validity": {
            "to": valid_until
        },
        "retrieved_at": datetime.utcnow().isoformat(),
        "count": len(pfz_locations),
        "pfz_locations": pfz_locations
    }

    # Insert the latest advisory
    result = collection.insert_one(document)

    return {
        "success": True,
        "mongo_id": str(result.inserted_id),
        "count": len(pfz_locations)
    }

def get_pfz_valid_until(page):
    """
    Extract the PFZ validity date from the live INCOIS page.
    """

    body_text = page.locator("body").inner_text()

    marker = "TILL "

    if marker not in body_text.upper():
        raise RuntimeError(
            "PFZ validity date was not found on the INCOIS page."
        )

    text_upper = body_text.upper()
    start = text_upper.index(marker) + len(marker)

    valid_until = body_text[start:start + 15].strip()

    return valid_until