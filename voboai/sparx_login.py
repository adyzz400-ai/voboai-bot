"""
VoboAi — Sparx Maths login diagnostic.

TEMPORARY diagnostic version.
This does NOT perform the actual login or homework automation.

It opens the Sparx school-selection page and reports:
- Page title and URL
- Visible page text
- All inputs/textareas
- All buttons
- Relevant attributes/classes
- Iframes/frames and their interactive elements
- Whether the expected school-search element exists
"""

import os
import time

# Keep Playwright browsers inside the deployed project environment.
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

from playwright.sync_api import sync_playwright


SELECT_URL = (
    "https://selectschool.sparx-learning.com/"
    "?app=sparx_maths&forget=1"
)


def describe_elements(page):
    """Print useful information about interactive elements."""

    print("\n" + "=" * 70)
    print("MAIN PAGE DIAGNOSTIC")
    print("=" * 70)

    print(f"URL: {page.url}")
    print(f"TITLE: {page.title()}")

    # Page text
    try:
        body_text = page.locator("body").inner_text(timeout=10000)
        print("\n--- VISIBLE PAGE TEXT ---")
        print(body_text[:5000])
    except Exception as e:
        print(f"\nCould not read page text: {e}")

    # Inputs / textareas / contenteditable
    print("\n--- INPUT ELEMENTS ---")

    try:
        inputs = page.locator(
            "input, textarea, [contenteditable='true']"
        ).evaluate_all(
            """
            elements => elements.map((el, index) => ({
                index: index,
                tag: el.tagName,
                type: el.getAttribute("type"),
                id: el.id,
                name: el.getAttribute("name"),
                class: el.className,
                placeholder: el.getAttribute("placeholder"),
                ariaLabel: el.getAttribute("aria-label"),
                role: el.getAttribute("role"),
                value: el.value || "",
                outerHTML: el.outerHTML.slice(0, 1000)
            }))
            """
        )

        if not inputs:
            print("NO INPUTS FOUND")

        for item in inputs:
            print("\nINPUT:")
            print(f"  index:       {item['index']}")
            print(f"  tag:         {item['tag']}")
            print(f"  type:        {item['type']}")
            print(f"  id:          {item['id']}")
            print(f"  name:        {item['name']}")
            print(f"  class:       {item['class']}")
            print(f"  placeholder: {item['placeholder']}")
            print(f"  aria-label:  {item['ariaLabel']}")
            print(f"  role:        {item['role']}")
            print(f"  value:       {item['value']}")
            print(f"  HTML:        {item['outerHTML']}")

    except Exception as e:
        print(f"INPUT DIAGNOSTIC ERROR: {e}")

    # Buttons
    print("\n--- BUTTON ELEMENTS ---")

    try:
        buttons = page.locator(
            "button, input[type='button'], input[type='submit']"
        ).evaluate_all(
            """
            elements => elements.map((el, index) => ({
                index: index,
                tag: el.tagName,
                type: el.getAttribute("type"),
                id: el.id,
                name: el.getAttribute("name"),
                class: el.className,
                text: el.innerText || el.value || "",
                ariaLabel: el.getAttribute("aria-label"),
                outerHTML: el.outerHTML.slice(0, 1000)
            }))
            """
        )

        if not buttons:
            print("NO BUTTONS FOUND")

        for item in buttons:
            print("\nBUTTON:")
            print(f"  index:      {item['index']}")
            print(f"  tag:        {item['tag']}")
            print(f"  type:       {item['type']}")
            print(f"  id:         {item['id']}")
            print(f"  name:       {item['name']}")
            print(f"  class:      {item['class']}")
            print(f"  text:       {item['text']}")
            print(f"  aria-label: {item['ariaLabel']}")
            print(f"  HTML:       {item['outerHTML']}")

    except Exception as e:
        print(f"BUTTON DIAGNOSTIC ERROR: {e}")

    # Iframes
    print("\n--- IFRAMES ---")

    try:
        iframe_count = page.locator("iframe").count()
        print(f"IFRAME COUNT: {iframe_count}")

        for i in range(iframe_count):
            iframe = page.locator("iframe").nth(i)

            print(f"\nIFRAME #{i}")
            print(f"  src:   {iframe.get_attribute('src')}")
            print(f"  id:    {iframe.get_attribute('id')}")
            print(f"  name:  {iframe.get_attribute('name')}")
            print(f"  class: {iframe.get_attribute('class')}")

    except Exception as e:
        print(f"IFRAME DIAGNOSTIC ERROR: {e}")

    # Expected selector checks
    print("\n--- EXPECTED SELECTOR CHECKS ---")

    selectors = [
        "input",
        "textarea",
        "[role='textbox']",
        "[contenteditable='true']",
        "input[type='search']",
        "input[type='text']",
        "[placeholder*='school' i]",
        "[placeholder*='search' i]",
        "[aria-label*='school' i]",
        "[aria-label*='search' i]",
        "._Input_1573n_4",
        ".sm-input",
    ]

    for selector in selectors:
        try:
            count = page.locator(selector).count()
            print(f"{selector}: {count}")
        except Exception as e:
            print(f"{selector}: ERROR - {e}")


def describe_frames(page):
    """Inspect every Playwright frame for inputs and buttons."""

    print("\n" + "=" * 70)
    print("FRAME DIAGNOSTIC")
    print("=" * 70)

    frames = page.frames

    print(f"TOTAL FRAMES: {len(frames)}")

    for index, frame in enumerate(frames):
        print("\n" + "-" * 60)
        print(f"FRAME #{index}")
        print(f"URL: {frame.url}")

        try:
            inputs = frame.locator(
                "input, textarea, [contenteditable='true']"
            ).evaluate_all(
                """
                elements => elements.map((el, index) => ({
                    index: index,
                    tag: el.tagName,
                    type: el.getAttribute("type"),
                    id: el.id,
                    name: el.getAttribute("name"),
                    class: el.className,
                    placeholder: el.getAttribute("placeholder"),
                    ariaLabel: el.getAttribute("aria-label"),
                    role: el.getAttribute("role"),
                    outerHTML: el.outerHTML.slice(0, 1000)
                }))
                """
            )

            print(f"INPUTS IN FRAME: {len(inputs)}")

            for item in inputs:
                print(
                    "  INPUT "
                    f"#{item['index']} | "
                    f"tag={item['tag']} | "
                    f"type={item['type']} | "
                    f"id={item['id']} | "
                    f"class={item['class']} | "
                    f"placeholder={item['placeholder']} | "
                    f"aria-label={item['ariaLabel']}"
                )

        except Exception as e:
            print(f"Could not inspect inputs: {e}")

        try:
            buttons = frame.locator(
                "button, input[type='button'], input[type='submit']"
            ).evaluate_all(
                """
                elements => elements.map((el, index) => ({
                    index: index,
                    tag: el.tagName,
                    type: el.getAttribute("type"),
                    id: el.id,
                    class: el.className,
                    text: el.innerText || el.value || "",
                    ariaLabel: el.getAttribute("aria-label")
                }))
                """
            )

            print(f"BUTTONS IN FRAME: {len(buttons)}")

            for item in buttons:
                print(
                    "  BUTTON "
                    f"#{item['index']} | "
                    f"tag={item['tag']} | "
                    f"type={item['type']} | "
                    f"id={item['id']} | "
                    f"class={item['class']} | "
                    f"text={item['text']} | "
                    f"aria-label={item['ariaLabel']}"
                )

        except Exception as e:
            print(f"Could not inspect buttons: {e}")


def login(
    username: str,
    password: str,
    school_name: str,
    headless: bool = True,
):
    """
    Diagnostic-only login function.

    The username/password/school arguments are intentionally not used yet.
    We first need to see exactly what Render receives from Sparx.
    """

    del username
    del password
    del school_name

    playwright = sync_playwright().start()
    browser = None

    try:
        print("\n" + "=" * 70)
        print("SPARX PLAYWRIGHT DIAGNOSTIC STARTING")
        print("=" * 70)

        print("\nLaunching Chromium...")

        browser = playwright.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        context = browser.new_context()
        page = context.new_page()

        print(f"\nOpening:\n{SELECT_URL}")

        page.goto(
            SELECT_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print("\nInitial page loaded.")
        print(f"URL: {page.url}")
        print(f"TITLE: {page.title()}")

        # Give Sparx's normal client-side page code a little time
        # to finish rendering before inspecting the DOM.
        print("\nWaiting 5 seconds for page rendering...")
        time.sleep(5)

        describe_elements(page)
        describe_frames(page)

        # Specific checks for the school input.
        print("\n" + "=" * 70)
        print("SCHOOL INPUT CHECK")
        print("=" * 70)

        checks = [
            (
                "get_by_role textbox",
                lambda: page.get_by_role(
                    "textbox",
                    name="Start typing your school's name",
                ).count(),
            ),
            (
                "get_by_placeholder",
                lambda: page.get_by_placeholder(
                    "Start typing your school's name"
                ).count(),
            ),
            (
                "placeholder partial",
                lambda: page.locator(
                    "[placeholder*=\"Start typing\"]"
                ).count(),
            ),
            (
                "hashed Sparx input class",
                lambda: page.locator(
                    "._Input_1573n_4"
                ).count(),
            ),
        ]

        for name, check in checks:
            try:
                print(f"{name}: {check()}")
            except Exception as e:
                print(f"{name}: ERROR - {e}")

        print("\n" + "=" * 70)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 70)

        print(
            "\nIMPORTANT: No login was attempted."
            "\nNo username or password was entered."
            "\nNo homework automation was started."
        )

        # Keep the browser alive briefly so Render has time to finish
        # writing the diagnostic output to its logs.
        time.sleep(2)

        browser.close()
        playwright.stop()

        return {
            "success": False,
            "diagnostic": True,
            "page": None,
            "browser": None,
            "context": None,
            "playwright": None,
            "url": SELECT_URL,
        }

    except Exception as e:
        print("\n" + "=" * 70)
        print("DIAGNOSTIC ERROR")
        print("=" * 70)
        print(str(e))

        try:
            if browser:
                browser.close()
        except Exception:
            pass

        try:
            playwright.stop()
        except Exception:
            pass

        raise


def close_login(result):
    """Compatibility function for the existing bot."""

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


if __name__ == "__main__":
    result = login(
        username="",
        password="",
        school_name="",
        headless=True,
    )

    print("\nDiagnostic finished.")
    print(f"URL checked: {result['url']}")