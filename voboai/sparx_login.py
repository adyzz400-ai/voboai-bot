"""
VoboAi — Sparx Maths login automation.

Real flow:
  1. Open Sparx school selection
  2. Search for school
  3. Select school
  4. Click Continue
  5. Wait for auth page
  6. Fill username/password
  7. Click Log in
"""

import os
import time

os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH",
    "/opt/render/.cache/ms-playwright",
)

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


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
    with sync_playwright() as p:
        print("[login] Starting Playwright...")

        browser = p.chromium.launch(
            headless=headless
        )

        print("[login] ✅ Chromium launched")

        context = browser.new_context()
        page = context.new_page()

        # Helpful diagnostics
        page.on(
            "console",
            lambda msg: print(
                f"[browser console] {msg.type}: {msg.text}"
            ),
        )

        page.on(
            "pageerror",
            lambda error: print(
                f"[browser page error] {error}"
            ),
        )

        # ---- Step 1: School select ----
        print(
            f"[login] Opening Sparx school selector..."
        )

        try:
            page.goto(
                SELECT_URL,
                wait_until="domcontentloaded",
                timeout=30000,
            )
        except PlaywrightTimeoutError:
            print(
                "[login] ⚠️ Initial page load timed out."
            )
            print(
                f"[login] Current URL: {page.url}"
            )
            print(
                f"[login] Current title: {page.title()}"
            )

        print(
            f"[login] URL after opening: {page.url}"
        )

        print(
            f"[login] Page title: {page.title()}"
        )

        # Detect protection/verification page
        title = page.title().lower()

        if (
            "just a moment" in title
            or "cloudflare" in page.content().lower()
        ):
            print(
                "[login] ⚠️ Sparx is showing a browser "
                "verification/protection page."
            )
            print(
                "[login] The school selector has not "
                "loaded yet."
            )

            return {
                "success": False,
                "error": (
                    "Sparx is showing a browser "
                    "verification/protection page."
                ),
                "page": page,
                "browser": browser,
                "context": context,
                "url": page.url,
            }

        # ---- Find school search box ----
        print(
            "[login] Looking for school search box..."
        )

        try:
            search = page.locator(
                "input[type='search'], "
                "input[type='text'], "
                "[role='searchbox']"
            ).first

            search.wait_for(
                state="visible",
                timeout=15000,
            )

            print(
                "[login] ✅ School search box found"
            )

        except PlaywrightTimeoutError:
            print(
                "[login] ❌ School search box was not found."
            )
            print(
                f"[login] URL: {page.url}"
            )
            print(
                f"[login] Title: {page.title()}"
            )

            return {
                "success": False,
                "error": (
                    "Sparx school search box "
                    "did not appear."
                ),
                "page": page,
                "browser": browser,
                "context": context,
                "url": page.url,
            }

        # ---- Type school ----
        print(
            f"[login] Typing school: {school_name}"
        )

        search.fill(school_name)

        print(
            "[login] ✅ School name entered"
        )

        time.sleep(2)

        # ---- Select school ----
        print(
            "[login] Looking for school result..."
        )

        try:
            page.locator(
                f"text={school_name}"
            ).first.click()

            print(
                "[login] ✅ Clicked school result"
            )

        except Exception as first_error:
            print(
                "[login] Normal school-result selector "
                "didn't work."
            )
            print(
                f"[login] Reason: {first_error}"
            )

            try:
                page.locator(
                    "li, [role='option'], button"
                ).filter(
                    has_text=school_name
                ).first.click()

                print(
                    "[login] ✅ Clicked school result "
                    "(fallback)"
                )

            except Exception as second_error:
                print(
                    "[login] ❌ Could not click school result."
                )
                print(
                    f"[login] Reason: {second_error}"
                )

                return {
                    "success": False,
                    "error": (
                        "School result appeared to be "
                        "missing or could not be clicked."
                    ),
                    "page": page,
                    "browser": browser,
                    "context": context,
                    "url": page.url,
                }

        # ---- Continue ----
        print(
            "[login] Looking for Continue button..."
        )

        try:
            continue_button = page.get_by_role(
                "button",
                name="Continue",
            )

            continue_button.wait_for(
                state="visible",
                timeout=10000,
            )

            continue_button.click()

            print(
                "[login] ✅ Clicked Continue"
            )

        except PlaywrightTimeoutError:
            print(
                "[login] ❌ Continue button was not found."
            )

            return {
                "success": False,
                "error": (
                    "Continue button did not appear."
                ),
                "page": page,
                "browser": browser,
                "context": context,
                "url": page.url,
            }

        # ---- Auth redirect ----
        print(
            "[login] Waiting for Sparx login page..."
        )

        try:
            page.wait_for_url(
                "**/oauth2/auth**",
                timeout=30000,
            )

            print(
                "[login] ✅ Redirected to authentication page"
            )

        except PlaywrightTimeoutError:
            print(
                "[login] ❌ Authentication page "
                "was not reached within 30 seconds."
            )
            print(
                f"[login] Current URL: {page.url}"
            )
            print(
                f"[login] Current title: {page.title()}"
            )

            return {
                "success": False,
                "error": (
                    "Sparx authentication page "
                    "was not reached."
                ),
                "page": page,
                "browser": browser,
                "context": context,
                "url": page.url,
            }

        # ---- Username ----
        print(
            "[login] Looking for username field..."
        )

        try:
            page.locator(
                "#username"
            ).wait_for(
                state="visible",
                timeout=15000,
            )

            page.fill(
                "#username",
                username,
            )

            print(
                "[login] ✅ Username entered"
            )

        except PlaywrightTimeoutError:
            print(
                "[login] ❌ Username field was not found."
            )

            return {
                "success": False,
                "error": (
                    "Username field did not appear."
                ),
                "page": page,
                "browser": browser,
                "context": context,
                "url": page.url,
            }

        # ---- Password ----
        print(
            "[login] Looking for password field..."
        )

        try:
            page.locator(
                "#password"
            ).wait_for(
                state="visible",
                timeout=15000,
            )

            page.fill(
                "#password",
                password,
            )

            print(
                "[login] ✅ Password entered"
            )

        except PlaywrightTimeoutError:
            print(
                "[login] ❌ Password field was not found."
            )

            return {
                "success": False,
                "error": (
                    "Password field did not appear."
                ),
                "page": page,
                "browser": browser,
                "context": context,
                "url": page.url,
            }

        # ---- Log in ----
        print(
            "[login] Looking for Log in button..."
        )

        try:
            login_button = page.get_by_role(
                "button",
                name="Log in",
            )

            login_button.wait_for(
                state="visible",
                timeout=10000,
            )

            login_button.click()

            print(
                "[login] ✅ Clicked Log in"
            )

        except PlaywrightTimeoutError:
            print(
                "[login] ❌ Log in button was not found."
            )

            return {
                "success": False,
                "error": (
                    "Log in button did not appear."
                ),
                "page": page,
                "browser": browser,
                "context": context,
                "url": page.url,
            }

        # ---- Final page ----
        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=30000,
            )
        except PlaywrightTimeoutError:
            print(
                "[login] ⚠️ Final page did not reach "
                "networkidle within 30 seconds."
            )

        time.sleep(3)

        final_url = page.url

        print(
            f"[login] Final URL: {final_url}"
        )

        print(
            f"[login] Final title: {page.title()}"
        )

        success = (
            "auth.sparx-learning.com"
            not in final_url
        )

        if success:
            print(
                "[login] ✅ Login appears successful"
            )
        else:
            print(
                "[login] ❌ Login appears unsuccessful"
            )

        return {
            "success": success,
            "page": page,
            "browser": browser,
            "context": context,
            "url": final_url,
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print(
            "Usage: python -m "
            "voboai.sparx_login "
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
    else:
        print(
            f"LOGIN FAILED -> "
            f"{result.get('error', 'unknown error')}"
        )