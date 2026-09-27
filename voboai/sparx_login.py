import os

from playwright.sync_api import sync_playwright

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

SCHOOL_URL = (
    "https://selectschool.sparx-learning.com/"
    "?app=sparx_maths&forget=1"
)


def _find_school_input(page):
    selectors = [
        'input[placeholder="Start typing your school\'s name..."]',
        'input[placeholder*="Start typing your school"]',
        'input[aria-label*="Start typing your school"]',
        'input[type="search"]',
        'input[type="text"]',
        '[role="textbox"]',
    ]

    for frame in page.frames:
        for selector in selectors:
            try:
                locator = frame.locator(selector).first

                if locator.count() > 0 and locator.is_visible():
                    return locator

            except Exception:
                pass

    return None


def login(username, password, school_name, headless=True):
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ],
    )

    context = browser.new_context(
        viewport={
            "width": 1280,
            "height": 900,
        }
    )

    page = context.new_page()

    try:
        print("[Sparx] Opening school selection page...")

        page.goto(
            SCHOOL_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print(f"[Sparx] Page loaded: {page.url}")

        page.wait_for_timeout(3000)

        print("[Sparx] Looking for school search box...")

        school_input = _find_school_input(page)

        if school_input is None:
            page.wait_for_timeout(3000)
            school_input = _find_school_input(page)

        if school_input is None:
            raise RuntimeError(
                "Could not find the Sparx school search box."
            )

        print("[Sparx] School search box found.")

        school_input.click()
        school_input.fill(school_name)

        print(
            f"[Sparx] Searching for school: {school_name}"
        )

        page.wait_for_timeout(2000)

        # Find the school result.
        school_result = None

        result_selectors = [
            f'text="{school_name}"',
            f'[role="option"]:has-text("{school_name}")',
            f'li:has-text("{school_name}")',
            f'button:has-text("{school_name}")',
        ]

        for frame in page.frames:
            for selector in result_selectors:
                try:
                    locator = frame.locator(selector).first

                    if (
                        locator.count() > 0
                        and locator.is_visible()
                    ):
                        school_result = locator
                        break

                except Exception:
                    pass

            if school_result:
                break

        if school_result:
            school_result.click()
            print("[Sparx] School selected.")
        else:
            print(
                "[Sparx] Exact school result not found; "
                "checking Continue."
            )

        # Continue button.
        continue_button = None

        for frame in page.frames:
            try:
                button = frame.get_by_role(
                    "button",
                    name="Continue",
                    exact=True,
                ).first

                if (
                    button.count() > 0
                    and button.is_visible()
                ):
                    continue_button = button
                    break

            except Exception:
                pass

        if continue_button is None:
            raise RuntimeError(
                "Could not find the Continue button."
            )

        continue_button.click()

        print("[Sparx] Continue clicked.")

        page.wait_for_timeout(2000)

        # Find username/password fields.
        username_input = None
        password_input = None

        for frame in page.frames:
            try:
                inputs = frame.locator("input")
                count = inputs.count()

                for i in range(count):
                    inp = inputs.nth(i)

                    if not inp.is_visible():
                        continue

                    input_type = inp.get_attribute("type")

                    if input_type == "password":
                        password_input = inp

                    elif (
                        input_type in (None, "text")
                        and username_input is None
                    ):
                        username_input = inp

            except Exception:
                pass

        if username_input is None:
            raise RuntimeError(
                "Could not find the Sparx username field."
            )

        if password_input is None:
            raise RuntimeError(
                "Could not find the Sparx password field."
            )

        username_input.fill(username)
        print("[Sparx] Username entered.")

        password_input.fill(password)
        print("[Sparx] Password entered.")

        # Log in button.
        login_button = None

        for frame in page.frames:
            try:
                button = frame.get_by_role(
                    "button",
                    name="Log in",
                    exact=True,
                ).first

                if (
                    button.count() > 0
                    and button.is_visible()
                ):
                    login_button = button
                    break

            except Exception:
                pass

        if login_button is None:
            raise RuntimeError(
                "Could not find the Log in button."
            )

        login_button.click()

        print("[Sparx] Log in clicked.")

        page.wait_for_timeout(3000)

        print(f"[Sparx] Final URL: {page.url}")

        return {
            "success": True,
            "page": page,
            "browser": browser,
            "context": context,
            "playwright": playwright,
        }

    except Exception as e:
        print(f"[Sparx] ERROR: {e}")

        try:
            browser.close()
        except Exception:
            pass

        try:
            playwright.stop()
        except Exception:
            pass

        return {
            "success": False,
            "error": str(e),
        }