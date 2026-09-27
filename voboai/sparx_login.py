"""
VoboAi — Sparx Maths login automation.
"""

import os
import time

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
    playwright = sync_playwright().start()
    browser = None
    step = "Starting Playwright"

    try:
        step = "Launching Chromium"

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
        # STEP 1 — Open school selection
        # ---------------------------------------------------------

        step = "Opening Sparx school selection page"

        print(f"[login] Opening school select: {SELECT_URL}")

        page.goto(
            SELECT_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print(f"[login] Page loaded: {page.url}")

        # ---------------------------------------------------------
        # STEP 2 — Find school search
        # ---------------------------------------------------------

        step = "Waiting for school search box"

search = page.get_by_role(
    "textbox",
    name="Start typing your school's name"
)

search.wait_for(
    state="visible",
    timeout=30000,
)

print("[login] Found Sparx school search box")

        # ---------------------------------------------------------
        # STEP 3 — Enter school name
        # ---------------------------------------------------------

        step = "Entering school name"

        search.click()
        search.fill(school_name)

        print(
            f"[login] Typed school: {school_name}"
        )

        time.sleep(2)

        # ---------------------------------------------------------
        # STEP 4 — Select school
        # ---------------------------------------------------------

        step = "Selecting school"

        try:
            page.get_by_text(
                school_name,
                exact=True,
            ).first.click()

            print(
                "[login] Clicked school result"
            )

        except Exception:
            page.locator(
                "li, "
                "[role='option'], "
                "button"
            ).filter(
                has_text=school_name
            ).first.click()

            print(
                "[login] Clicked school result (fallback)"
            )

        # ---------------------------------------------------------
        # STEP 5 — Continue
        # ---------------------------------------------------------

        step = "Clicking Continue"

        page.get_by_role(
            "button",
            name="Continue",
        ).click()

        print(
            "[login] Clicked Continue"
        )

        step = "Waiting for Sparx login page"

        try:
            page.wait_for_url(
                "**/oauth2/auth**",
                timeout=30000,
            )
        except Exception:
            time.sleep(3)

        print(
            f"[login] Current URL: {page.url}"
        )

        # ---------------------------------------------------------
        # STEP 6 — Username
        # ---------------------------------------------------------

        step = "Waiting for username field"

        username_field = page.locator(
            "#username"
        )

        username_field.wait_for(
            state="visible",
            timeout=30000,
        )

        step = "Entering username"

        username_field.fill(username)

        print(
            "[login] Filled username from Discord modal"
        )

        # ---------------------------------------------------------
        # STEP 7 — Password
        # ---------------------------------------------------------

        step = "Waiting for password field"

        password_field = page.locator(
            "#password"
        )

        password_field.wait_for(
            state="visible",
            timeout=30000,
        )

        step = "Entering password"

        password_field.fill(password)

        print(
            "[login] Filled password from Discord modal"
        )

        # ---------------------------------------------------------
        # STEP 8 — Log in
        # ---------------------------------------------------------

        step = "Clicking Log in"

        page.get_by_role(
            "button",
            name="Log in",
        ).click()

        print(
            "[login] Clicked Log in"
        )

        step = "Waiting for login to complete"

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
        # STEP 9 — Verify session
        # ---------------------------------------------------------

        step = "Verifying Sparx session"

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
            browser.close()
            playwright.stop()

            return {
                "success": False,
                "page": None,
                "browser": None,
                "context": None,
                "playwright": None,
                "url": final_url,
                "error": "Login could not be verified.",
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

    except Exception as e:

        error_message = (
            f"Step: {step}\n"
            f"URL: "
            f"{page.url if browser and 'page' in locals() else 'Unavailable'}\n"
            f"Error: {str(e)}"
        )

        print(
            f"[login] ERROR\n{error_message}"
        )

        try:
            if browser:
                browser.close()
        except Exception:
            pass

        try:
            playwright.stop()
        except Exception:
            pass

        raise RuntimeError(
            error_message
        ) from e


def close_login(result):
    """
    Close the browser returned by login().
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