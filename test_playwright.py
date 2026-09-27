import os

os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH",
    "/opt/render/.cache/ms-playwright"
)

from playwright.sync_api import sync_playwright

SPARX_URL = (
    "https://selectschool.sparx-learning.com/"
    "?app=sparx_maths&forget=1"
)

print("Starting Playwright test...")

with sync_playwright() as p:
    print("Playwright loaded.")
    print("Chromium path:")
    print(p.chromium.executable_path)

    browser = p.chromium.launch(headless=True)
    print("✅ Chromium launched successfully!")

    page = browser.new_page()
    page.goto(SPARX_URL, wait_until="networkidle")

    print("✅ Sparx page loaded!")
    print("Page title:", page.title())
    print("URL:", page.url)

    browser.close()

print("✅ TEST PASSED")