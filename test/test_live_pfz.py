import requests

PAGE_URL = "https://www.incois.gov.in/MarineFisheries/TextData?secid=SEC007"

FORECAST_URL = (
    "https://www.incois.gov.in/MarineFisheries/"
    "formattedForecast.action"
)

headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8,ta;q=0.7",
    "Referer": PAGE_URL,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-CH-UA": '"Chromium";v="152", "Not?A_Brand";v="24", "Microsoft Edge";v="152"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0.0.0 Safari/537.36 Edg/152.0.0.0"
    ),
}

with requests.Session() as session:

    print("Step 1: Opening Text Data page...")

    page_response = session.get(
        PAGE_URL,
        headers=headers,
        timeout=30
    )

    print("Page status:", page_response.status_code)
    print("Final URL:", page_response.url)

    print("\nCookies received:")
    print(session.cookies.get_dict())

    print("\nStep 2: Calling formattedForecast.action...")

    params = {
        "distanceformat": "km",
        "depthformat": "metre",
        "latlongformat": "dms",
    }

    response = session.get(
        FORECAST_URL,
        params=params,
        headers=headers,
        timeout=30
    )

    print("\nForecast status:", response.status_code)
    print("Forecast URL:", response.url)

    print("\nResponse:")
    print(response.text[:5000])