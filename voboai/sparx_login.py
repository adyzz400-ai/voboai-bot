import os

from playwright.sync_api import sync_playwright


os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

SCHOOL_URL = (
    "https://selectschool.sparx-learning.com/"
    "?app=sparx_maths&forget=1"
)


def _find_school_input(page):
    # Exact placeholder shown on the Sparx page.
    exact = "Start typing your school's name..."

    # Try the main page first.
    locators = [
        page.get_by_placeholder(exact, exact=True),
        page.locator(f'input[placeholder="{exact}"]'),
        page.locator("input").filter(
            has=page.locator(
                '[placeholder*="Start typing"]'
            )
        ),
    ]

    for locator in locators:
        try:
            if locator.count() > 0:
                item = locator.first
                item.wait_for(
                    state="visible",
                    timeout=15000,
                )
                return item
        except Exception:
            pass

    # Then check every iframe.
    for frame in page.frames:
        if frame == page.main_frame:
            continue

        try:
            locator = frame.get_by_placeholder(
                exact,
                exact=True,
            )

            if locator.count() > 0:
                item = locator.first
                item.wait_for(
                    state="visible",
                    timeout=10000,
                )
                return item

        except Exception:
            pass

        try:
            locator = frame.locator(
                'input[placeholder*="Start typing"]'
            )

            if locator.count() > 0:
                item = locator.first
                item.wait_for(
                    state="visible",
                    timeout=10000,
                )
                return item

        except Exception:
            pass

    return None


def _find_button(page, name):
    # Main page.
    try:
        button = page.get_by_role(
            "button",
            name=name,
            exact=True,
        ).first

        if button.count() > 0:
            button.wait_for(
                state="visible",
                timeout=10000,
            )
            return button
    except Exception:
        pass

    # Frames.
    for frame in page.frames:
        if frame == page.main_frame:
            continue

        try:
            button = frame.get_by_role(
                "button",
                name=name,
                exact=True,
            ).first

            if button.count() > 0:
                button.wait_for(
                    state="visible",
                    timeout=10000,
                )
                return button
        except Exception:
            pass

    return None


def login(
    username,
    password,
    school_name,
    headless=True,
):
    playwright = sync_playwright().start()

    browser = None

    try:
        browser = playwright.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        context = browser.new_context(
            viewport={
                "width": 1280,
                "height": 900,
            },
        )

        page = context.new_page()

        # Open Sparx.
        page.goto(
            SCHOOL_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        # Give the page's JavaScript time to render.
        page.wait_for_timeout(3000)

        # Find school input.
        school_input = _find_school_input(page)

        if school_input is None:
            raise RuntimeError(
                "Sparx school input was not visible to Playwright."
            )

        # Enter school name.
        school_input.click()
        school_input.fill(school_name)

        page.wait_for_timeout(2000)

        # Try to select the matching school.
        school_result = None

        result_patterns = [
            f'[role="option"]:has-text("{school_name}")',
            f'li:has-text("{school_name}")',
            f'button:has-text("{school_name}")',
            f'div:has-text("{school_name}")',
        ]

        for frame in page.frames:
            for selector in result_patterns:
                try:
                    results = frame.locator(selector)

                    count = results.count()

                    for i in range(min(count, 10)):
                        result = results.nth(i)

                        if result.is_visible():
                            school_result = result
                            break

                    if school_result:
                        break

                except Exception:
                    pass

            if school_result:
                break

        if school_result:
            school_result.click()
            page.wait_for_timeout(500)

        # Continue.
        continue_button = _find_button(
            page,
            "Continue",
        )

        if continue_button is None:
            raise RuntimeError(
                "Could not find the Sparx Continue button."
            )

        continue_button.click()

        page.wait_for_timeout(3000)

        # Find username/password.
        username_input = None
        password_input = None

        for frame in page.frames:
            try:
                inputs = frame.locator("input")

                for i in range(inputs.count()):
                    field = inputs.nth(i)

                    try:
                        if not field.is_visible():
                            continue
                    except Exception:
                        continue

                    field_type = (
                        field.get_attribute("type")
                        or ""
                    ).lower()

                    if field_type == "password":
                        password_input = field

                    elif field_type in (
                        "",
                        "text",
                    ):
                        if username_input is None:
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

        username_input.fill(username)
        password_input.fill(password)

        # Login.
        login_button = _find_button(
            page,
            "Log in",
        )

        if login_button is None:
            # Some Sparx pages use "Login".
            login_button = _find_button(
                page,
                "Login",
            )

        if login_button is None:
            raise RuntimeError(
                "Could not find the Sparx login button."
            )

        login_button.click()

        page.wait_for_timeout(4000)

        return {
            "success": True,
            "page": page,
            "browser": browser,
            "context": context,
            "playwright": playwright,
        }

    except Exception as e:
        if browser:
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