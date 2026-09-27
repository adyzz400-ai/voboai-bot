"""
VoboAi — Sparx Maths login automation.

Flow:
  1. Open Sparx school selection.
  2. Search/select school.
  3. Continue to Sparx authentication.
  4. Fill username/password.
  5. Log in.
  6. Verify the Sparx session.
  7. Keep the Playwright browser/page alive so homework.py
     can continue using the authenticated page.
"""

import os
import time

# Use Playwright's local browser installation.
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

from playwright.sync_api import sync_playwright


SELECT_URL = (
    "https://selectschool.sparx-learning.com/"
    "?app=sparx_maths&forget=1"
)


def login(
    username: str,
    password: str,
    school_name: str,
    headless: bool = True,
):
    """
    Log into Sparx and return a live authenticated browser/page.

    IMPORTANT:
    The Playwright manager is intentionally kept alive after this
    function returns because homework.py needs to use the page.
    """

    playwright = sync_playwright().start()

    try:
        browser = playwright.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        context = browser.new_context()
        page = context.new_page()

        # ---------------------------------------------------------
        # STEP 1 — School selection
        # ---------------------------------------------------------

        print(f"[login] Opening school select: {SELECT_URL}")

        page.goto(
            SELECT_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print(f"[login] Page loaded: {page.url}")

        search = page.locator(
            "input[type='search'], "
            "input[type='text'], "
            "[role='searchbox']"
        ).first

        search.wait_for(
            state="visible",
            timeout=30000,
        )

        search.fill(school_name)

        print(f"[login] Typed school: {school_name}")

        time.sleep(2)

        try:
            page.get_by_text(
                school_name,
                exact=True,
            ).first.click()

            print("[login] Clicked school result")

        except Exception:
            page.locator(
                "li, [role='option'], button"
            ).filter(
                has_text=school_name
            ).first.click()

            print(
                "[login] Clicked school result (fallback)"
            )

        # ---------------------------------------------------------
        # STEP 2 — Continue
        # ---------------------------------------------------------

        page.get_by_role(
            "button",
            name="Continue",
        ).click()

        print("[login] Clicked Continue")

        try:
            page.wait_for_url(
                "**/oauth2/auth**",
                timeout=30000,
            )
        except Exception:
            time.sleep(3)

        print(f"[login] Current URL: {page.url}")

        # ---------------------------------------------------------
        # STEP 3 — Username/password
        # ---------------------------------------------------------

        username_field = page.locator("#username")

        password_field = page.locator("#password")

        username_field.wait_for(
            state="visible",
            timeout=30000,
        )

        password_field.wait_for(
            state="visible",
            timeout=30000,
        )

        username_field.fill(username)

        print("[login] Filled username")

        password_field.fill(password)

        print("[login] Filled password")

        # ---------------------------------------------------------
        # STEP 4 — Login
        # ---------------------------------------------------------

        page.get_by_role(
            "button",
            name="Log in",
        ).click()

        print("[login] Clicked Log in")

        try:
            page.wait_for_load_state(
                "domcontentloaded",
                timeout=30000,
            )
        except Exception:
            pass

        time.sleep(3)

        final_url = page.url

        print(
            f"[login] Final URL: {final_url}"
        )

        # ---------------------------------------------------------
        # STEP 5 — Verify session
        # ---------------------------------------------------------

        cookies = context.cookies()

        cookie_names = {
            cookie["name"]
            for cookie in cookies
        }

        has_session = (
            "spxlrn_session" in cookie_names
            or "live_ssoprovider_session" in cookie_names
        )

        print(
            "[login] Session cookies:",
            ", ".join(sorted(cookie_names)),
        )

        left_auth = (
            "auth.sparx-learning.com"
            not in final_url
        )

        success = (
            left_auth
            or has_session
        )

        if not success:
            print(
                "[login] Login could not be verified."
            )

            browser.close()
            playwright.stop()

            return {
                "success": False,
                "page": None,
                "browser": None,
                "context": None,
                "playwright": None,
                "url": final_url,
            }

        print(
            "[login] Login successful."
        )

        return {
            "success": True,
            "page": page,
            "browser": browser,
            "context": context,
            "playwright": playwright,
            "url": final_url,
        }

    except Exception:
        try:
            browser.close()
        except Exception:
            pass

        try:
            playwright.stop()
        except Exception:
            pass

        raise


def close_login(result):
    """
    Close the browser returned by login().

    Call this after homework automation has completely finished.
    """

    try:
        result["browser"].close()
    except Exception:
        pass

    try:
        result["playwright"].stop()
    except Exception:
        pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print(
            "Usage: python -m voboai.sparx_login "
            "<username> <password> <school>"
        )
        sys.exit(1)

    result = login(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        headless=False,
    )

    if result["success"]:
        print(
            f"LOGIN OK -> {result['url']}"
        )

        input(
            "Press Enter to close the browser..."
        )

        close_login(result)

    else:
        print(
            f"LOGIN FAILED -> {result.get('url')}"
        )