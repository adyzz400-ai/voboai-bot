import os

from playwright.sync_api import sync_playwright


# Keep Playwright browsers inside the project environment.
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

SCHOOL_URL = (
    "https://selectschool.sparx-learning.com/"
    "?app=sparx_maths&forget=1"
)


def _get_school_input(page):
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

                if locator.count() > 0:
                    try:
                        locator.wait_for(
                            state="visible",
                            timeout=8000,
                        )
                        return locator
                    except Exception:
                        pass

            except Exception:
                pass

    return None


def _get_button(page, name):
    for frame in page.frames:
        try:
            button = frame.get_by_role(
                "button",
                name=name,
                exact=True,
            ).first

            if button.count() > 0:
                try:
                    button.wait_for(
                        state="visible",
                        timeout=8000,
                    )
                    return button
                except Exception:
                    pass

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
        # Open Sparx school selection.
        page.goto(
            SCHOOL_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=30000,
            )
        except Exception:
            # Some pages keep network requests open.
            pass

        # Find school search box.
        school_input = _get_school_input(page)

        if school_input is None:
            raise RuntimeError(
                "Could not find the Sparx school search box."
            )

        # Enter school.
        school_input.fill(school_name)

        page.wait_for_timeout(1500)

        # Find matching school.
        school_result = None

        result_selectors = [
            f'[role="option"]:has-text("{school_name}")',
            f'li:has-text("{school_name}")',
            f'button:has-text("{school_name}")',
        ]

        for frame in page.frames:
            for selector in result_selectors:
                try:
                    result = frame.locator(selector).first

                    if result.count() > 0:
                        try:
                            result.wait_for(
                                state="visible",
                                timeout=5000,
                            )

                            school_result = result
                            break

                        except Exception:
                            pass

                except Exception:
                    pass

            if school_result:
                break

        if school_result:
            school_result.click()

        # Continue to login.
        continue_button = _get_button(
            page,
            "Continue",
        )

        if continue_button is None:
            raise RuntimeError(
                "Could not find the Continue button."
            )

        continue_button.click()

        page.wait_for_timeout(2500)

        # Find username and password fields.
        username_input = None
        password_input = None

        for frame in page.frames:
            try:
                inputs = frame.locator("input")

                for i in range(inputs.count()):
                    field = inputs.nth(i)

                    try:
                        field.wait_for(
                            state="visible",
                            timeout=1500,
                        )
                    except Exception:
                        continue

                    input_type = field.get_attribute(
                        "type"
                    )

                    if input_type == "password":
                        password_input = field

                    elif (
                        input_type in (None, "text")
                        and username_input is None
                    ):
                        username_input = field

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

        # Enter credentials.
        username_input.fill(username)
        password_input.fill(password)

        # Log in.
        login_button = _get_button(
            page,
            "Log in",
        )

        if login_button is None:
            raise RuntimeError(
                "Could not find the Log in button."
            )

        login_button.click()

        page.wait_for_timeout(3000)

        return {
            "success": True,
            "page": page,
            "browser": browser,
            "context": context,
            "playwright": playwright,
        }

    except Exception as e:
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