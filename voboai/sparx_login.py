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


def _find_school_input(page):
    selectors = [
        "input[placeholder*='Start typing your school's name']",
        "input[aria-label*='Start typing your school's name']",
        "input[type='search']",
        "input[type='text']",
        "._Input_1573n_4",
        ".sm-input",
        "[role='textbox']",
    ]

    for frame in page.frames:
        for selector in selectors:
            try:
                locator = frame.locator(selector).first

                if locator.count() > 0:
                    locator.wait_for(
                        state="visible",
                        timeout=3000
                    )
                    return frame, locator

            except Exception:
                continue

    return None, None


def _find_school_result(frame, school_name):
    selectors = [
        f"text={school_name}",
        f"li:has-text('{school_name}')",
        f"[role='option']:has-text('{school_name}')",
        f"button:has-text('{school_name}')",
        "._SchoolResult_1h7n6_1",
    ]

    for selector in selectors:
        try:
            locator = frame.locator(selector).first

            if locator.count() > 0:
                locator.wait_for(
                    state="visible",
                    timeout=5000
                )
                return locator

        except Exception:
            continue

    return None


def login(
    username: str,
    password: str,
    school_name: str,
    headless: bool = True,
):
    playwright = sync_playwright().start()
    browser = None
    page = None
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

        print("[Sparx] Opening school selection page...")

        step = "Opening Sparx school selection page"

        page.goto(
            SELECT_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print(f"[Sparx] Page loaded: {page.url}")

        time.sleep(3)

        # --------------------------------------------------
        # SCHOOL SEARCH
        # --------------------------------------------------

        step = "Waiting for school search box"

        frame, search = _find_school_input(page)

        if search is None:
            raise RuntimeError(
                "Could not find the Sparx school search box."
            )

        print("[Sparx] School search box found.")

        # --------------------------------------------------
        # ENTER SCHOOL
        # --------------------------------------------------

        step = "Entering school name"

        search.click()
        search.fill(school_name)

        print(f"[Sparx] Searching for school: {school_name}")

        time.sleep(2)

        # --------------------------------------------------
        # SELECT SCHOOL
        # --------------------------------------------------

        step = "Selecting school"

        result = _find_school_result(
            frame,
            school_name
        )

        if result is None:
            result = _find_school_result(
                page.main_frame,
                school_name
            )

        if result is None:
            raise RuntimeError(
                f"Could not find school result for '{school_name}'."
            )

        result.click()

        print("[Sparx] School selected.")

        # --------------------------------------------------
        # CONTINUE
        # --------------------------------------------------

        step = "Clicking Continue"

        continue_button = page.get_by_role(
            "button",
            name="Continue"
        ).first

        if continue_button.count() == 0:
            continue_button = page.locator(
                "button:has-text('Continue')"
            ).first

        continue_button.wait_for(
            state="visible",
            timeout=15000
        )

        continue_button.click()

        print("[Sparx] Continue clicked.")

        # --------------------------------------------------
        # WAIT FOR LOGIN PAGE
        # --------------------------------------------------

        step = "Waiting for login page"

        time.sleep(3)

        print(f"[Sparx] Login page URL: {page.url}")

        # --------------------------------------------------
        # USERNAME
        # --------------------------------------------------

        step = "Waiting for username field"

        username_field = page.locator(
            "#username"
        ).first

        if username_field.count() == 0:
            username_field = page.locator(
                "input[name='username'], input[type='text']"
            ).first

        username_field.wait_for(
            state="visible",
            timeout=30000
        )

        username_field.fill(username)

        print("[Sparx] Username entered.")

        # --------------------------------------------------
        # PASSWORD
        # --------------------------------------------------

        step = "Waiting for password field"

        password_field = page.locator(
            "#password"
        ).first

        if password_field.count() == 0:
            password_field = page.locator(
                "input[name='password'], input[type='password']"
            ).first

        password_field.wait_for(
            state="visible",
            timeout=30000
        )

        password_field.fill(password)

        print("[Sparx] Password entered.")

        # --------------------------------------------------
        # LOGIN
        # --------------------------------------------------

        step = "Clicking Log in"

        login_button = page.get_by_role(
            "button",
            name="Log in"
        ).first

        if login_button.count() == 0:
            login_button = page.locator(
                ".sm-button.login-button, "
                "button:has-text('Log in')"
            ).first

        login_button.wait_for(
            state="visible",
            timeout=15000
        )

        login_button.click()

        print("[Sparx] Log in clicked.")

        # --------------------------------------------------
        # WAIT
        # --------------------------------------------------

        step = "Waiting for login to complete"

        try:
            page.wait_for_load_state(
                "domcontentloaded",
                timeout=30000
            )
        except Exception:
            pass

        time.sleep(3)

        print(f"[Sparx] Final URL: {page.url}")

        # --------------------------------------------------
        # CHECK SESSION
        # --------------------------------------------------

        step = "Checking login session"

        cookies = context.cookies()

        cookie_names = {
            cookie["name"]
            for cookie in cookies
        }

        print(
            "[Sparx] Cookies:",
            ", ".join(sorted(cookie_names))
        )

        # If we're no longer on the authentication page,
        # treat the login as successful.
        success = (
            "auth.sparx-learning.com" not in page.url
        )

        if not success:
            return {
                "success": False,
                "page": None,
                "browser": None,
                "context": None,
                "playwright": None,
                "url": page.url,
                "error": "Sparx login could not be verified.",
            }

        print("[Sparx] Login successful.")

        return {
            "success": True,
            "page": page,
            "browser": browser,
            "context": context,
            "playwright": playwright,
            "url": page.url,
        }

    except Exception as e:

        error = (
            f"Step: {step}\n"
            f"URL: {page.url if page else 'Unavailable'}\n"
            f"Error: {str(e)}"
        )

        print("[Sparx] ERROR")
        print(error)

        try:
            if browser:
                browser.close()
        except Exception:
            pass

        try:
            playwright.stop()
        except Exception:
            pass

        raise RuntimeError(error) from e


def close_login(result):
    try:
        if result.get("browser"):
            result["browser"].close()
    except Exception:
        pass

    try:
        if result.get("playwright"):
            result["playwright"].stop()
    except Exception:
        pass