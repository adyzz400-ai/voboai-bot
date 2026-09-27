import os

from playwright.sync_api import sync_playwright


def login(
    username,
    password,
    school_name,
    headless=True,
):
    playwright = None
    browser = None

    try:
        playwright = sync_playwright().start()

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
            }
        )

        page = context.new_page()

        school_url = (
            "https://selectschool.sparx-learning.com/"
            "?app=sparx_maths&forget=1"
        )

        page.goto(
            school_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(3000)

        school_input = page.locator(
            'input[placeholder="Start typing your school\'s name..."]'
        ).first

        school_input.wait_for(
            state="visible",
            timeout=30000,
        )

        school_input.fill(school_name)

        page.wait_for_timeout(2000)

        # Select the matching school.
        school_options = page.locator(
            '[role="option"], li, button'
        )

        school_selected = False

        count = min(
            school_options.count(),
            50,
        )

        for i in range(count):
            try:
                option = school_options.nth(i)

                if not option.is_visible():
                    continue

                text = option.inner_text().strip()

                if school_name.lower() in text.lower():
                    option.click()
                    school_selected = True
                    break

            except Exception:
                continue

        if not school_selected:
            raise Exception(
                f"Could not select school: {school_name}"
            )

        continue_button = page.get_by_role(
            "button",
            name="Continue",
            exact=True,
        ).first

        continue_button.wait_for(
            state="visible",
            timeout=30000,
        )

        continue_button.click()

        page.wait_for_timeout(3000)

        # Find username and password fields.
        username_input = None
        password_input = None

        inputs = page.locator("input")

        count = inputs.count()

        for i in range(count):
            try:
                field = inputs.nth(i)

                if not field.is_visible():
                    continue

                field_type = (
                    field.get_attribute("type") or ""
                ).lower()

                if field_type == "password":
                    password_input = field

                elif field_type in ("", "text") and username_input is None:
                    username_input = field

            except Exception:
                continue

        if username_input is None:
            raise Exception(
                "Could not find the Sparx username field."
            )

        if password_input is None:
            raise Exception(
                "Could not find the Sparx password field."
            )

        username_input.fill(username)
        password_input.fill(password)

        login_button = page.get_by_role(
            "button",
            name="Log in",
            exact=True,
        ).first

        if login_button.count() == 0:
            login_button = page.get_by_role(
                "button",
                name="Login",
                exact=True,
            ).first

        login_button.wait_for(
            state="visible",
            timeout=30000,
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

        if playwright:
            try:
                playwright.stop()
            except Exception:
                pass

        return {
            "success": False,
            "error": str(e),
        }
