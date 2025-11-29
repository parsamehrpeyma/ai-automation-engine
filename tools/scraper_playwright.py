from playwright.sync_api import sync_playwright

def scrape_plain_text(url: str) -> str:
    """
    Scrape readable text from a webpage using Playwright.
    This function loads the page, removes all scripts, ads, and hidden elements,
    and extracts only the visible text content.
    """

    with sync_playwright() as p:
        # Launch Chromium browser in headless mode (no GUI)
        browser = p.chromium.launch(headless=True)

        # Open a new browser tab
        page = browser.new_page()

        # Navigate to the target URL
        page.goto(url, timeout=60000, wait_until="networkidle")

        # Extract all visible text from the page's <body>
        text = page.inner_text("body")

        # Close the browser
        browser.close()

        return text
