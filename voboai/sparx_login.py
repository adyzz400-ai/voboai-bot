import os
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

SCHOOL_URL = "https://selectschool.sparx-learning.com/?app=sparx_maths&forget=1"


async def _find_school_input(page):
    selectors = [
        'input[placeholder="Start typing your school\'s name..."]',
        'input[placeholder*="Start typing your school"]',
        'input[aria-label*="Start typing your school"]',
        'input[type="search"]',
        'input[type="text"]',
        '[role="textbox"]',
    ]

    # Check every frame, including the main page.
    for frame in page.frames:
        for selector in selectors:
            try:
                locator = frame.locator(selector).first

                if await locator.count() > 0 and await locator.is_visible():
                    return locator

            except Exception:
                pass

    return None


async def login(username, password, school_name, headless=True):
    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ],
    )

    context = await browser.new_context(
        viewport={"width": 1280, "height": 900},
    )

    page = await context.new_page()

    try:
        print("[Sparx] Opening school selection page...")

        await page.goto(
            SCHOOL_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print(f"[Sparx] Page loaded: {page.url}")

        # Give Sparx's frontend time to initialise.
        await page.wait_for_timeout(2000)

        print("[Sparx] Looking for school search box...")

        school_input = await _find_school_input(page)

        if school_input is None:
            # One extra wait in case the frontend renders late.
            await page.wait_for_timeout(3000)
            school_input = await _find_school_input(page)

        if school_input is None:
            raise RuntimeError(
                "Could not find the Sparx school search box."
            )

        print("[Sparx] School search box found.")

        await school_input.click()
        await school_input.fill(school_name)

        print(f"[Sparx] Searching for school: {school_name}")

        await page.wait_for_timeout(2000)

        # Find the matching school result.
        result_selectors = [
            f'text="{school_name}"',
            f'[role="option"]:has-text("{school_name}")',
            f'li:has-text("{school_name}")',
            f'button:has-text("{school_name}")',
        ]

        school_result = None

        for frame in page.frames:
            for selector in result_selectors:
                try:
                    locator = frame.locator(selector).first

                    if await locator.count() > 0 and await locator.is_visible():
                        school_result = locator
                        break
                except Exception:
                    pass

            if school_result:
                break

        if school_result:
            await school_result.click()
            print("[Sparx] School selected.")
        else:
            print("[Sparx] No exact school result found; checking Continue.")

        # Continue button
        continue_button = None

        for frame in page.frames:
            try:
                button = frame.get_by_role(
                    "button",
                    name="Continue",
                    exact=True,
                ).first

                if await button.count() > 0 and await button.is_visible():
                    continue_button = button
                    break
            except Exception:
                pass

        if continue_button is None:
            raise RuntimeError("Could not find the Continue button.")

        await continue_button.click()

        print("[Sparx] Continue clicked.")

        await page.wait_for_timeout(2000)

        # Username
        username_input = None
        password_input = None

        for frame in page.frames:
            try:
                inputs = frame.locator("input")

                count = await inputs.count()

                for i in range(count):
                    inp = inputs.nth(i)

                    if not await inp.is_visible():
                        continue

                    input_type = await inp.get_attribute("type")
                    placeholder = await inp.get_attribute("placeholder")

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
            raise RuntimeError("Could not find the Sparx username field.")

        if password_input is None:
            raise RuntimeError("Could not find the Sparx password field.")

        await username_input.fill(username)
        print("[Sparx] Username entered.")

        await password_input.fill(password)
        print("[Sparx] Password entered.")

        # Login button
        login_button = None

        for frame in page.frames:
            try:
                button = frame.get_by_role(
                    "button",
                    name="Log in",
                    exact=True,
                ).first

                if await button.count() > 0 and await button.is_visible():
                    login_button = button
                    break
            except Exception:
                pass

        if login_button is None:
            raise RuntimeError("Could not find the Log in button.")

        await login_button.click()

        print("[Sparx] Log in clicked.")

        await page.wait_for_timeout(3000)

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

        await browser.close()
        await playwright.stop()

        return {
            "success": False,
            "error": str(e),
        }