from playwright.sync_api import sync_playwright


with sync_playwright() as p:

    print("Connecting to existing Edge...")

    browser = p.chromium.connect_over_cdp(
        "http://127.0.0.1:9222"
    )

    context = browser.contexts[0]

    # Find the PFZ Text Data page
    page = None

    for pge in context.pages:
        if "TextData" in pge.url:
            page = pge
            break

    if page is None:
        print("PFZ Text Data page not found.")
        browser.close()
        raise SystemExit

    print("Connected to PFZ page!")
    print("URL:", page.url)

    # Find the actual element that calls formatter()
    formatter_element = page.locator(
        '[onclick*="formatter"]'
    ).first

    print("\nFormatter element found.")

    print(
        "Tag:",
        formatter_element.evaluate("(el) => el.tagName")
    )

    print(
        "Onclick:",
        formatter_element.get_attribute("onclick")
    )

    # Listen for the actual PFZ request
    print("\nWaiting for formattedForecast.action...")

    with page.expect_response(
        lambda response:
            "formattedForecast.action" in response.url
            and response.status == 200,
        timeout=30000
    ) as response_info:

        print("Clicking formatter element...")

        formatter_element.click()

    response = response_info.value

    print("\nSUCCESS!")
    print("Response URL:")
    print(response.url)

    print("\nStatus:")
    print(response.status)

    html = response.text()

    print("\nResponse length:")
    print(len(html))

    print("\nFIRST 5000 CHARACTERS:")
    print(html[:5000])

    # Save response for inspection
    with open(
        "test/pfz_live_response.html",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(html)

    print("\nSaved response to:")
    print("test/pfz_live_response.html")

    input("\nPress ENTER to finish...")

    browser.close()