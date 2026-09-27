"""
VoboAi — Sparx Maths login automation.

Real flow (from user's actual page elements):
  1. School select page:
       https://selectschool.sparx-learning.com/?app=sparx_maths&forget=1
       - Type school name into the search box
       - Click the matching result
       - Click "Continue"
     This redirects to the auth page.
  2. Auth page:
       https://auth.sparx-learning.com/oauth2/auth?client_id=sparx-learning&hd=<school-uuid>&...
       - Fill #username
       - Fill #password
       - Click "Log in"
"""
import time

from playwright.sync_api import sync_playwright

SELECT_URL = "https://selectschool.sparx-learning.com/?app=sparx_maths&forget=1"


def login(username: str, password: str, school_name: str, headless: bool = True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        # ---- Step 1: School select ----
        print(f"[login] Opening school select: {SELECT_URL}")
        page.goto(SELECT_URL, wait_until="networkidle")

        # Type school name into the search box
        search = page.locator("input[type='search'], input[type='text'], [role='searchbox']").first
        search.fill(school_name)
        print(f"[login] Typed school: {school_name}")
        time.sleep(2)

        # Click the matching school result (a list item / button with the name)
        try:
            page.locator(f"text={school_name}").first.click()
            print("[login] Clicked school result")
        except Exception:
            page.locator("li, [role='option'], button").filter(has_text=school_name).first.click()
            print("[login] Clicked school result (fallback)")

        # Click Continue
        page.get_by_role("button", name="Continue").click()
        print("[login] Clicked Continue")

        # Wait for redirect to auth page
        page.wait_for_url("**/oauth2/auth**", timeout=30000)
        print(f"[login] Redirected to: {page.url}")

        # ---- Step 2: Fill login form ----
        page.fill("#username", username)
        print("[login] Filled username")

        page.fill("#password", password)
        print("[login] Filled password")

        page.get_by_role("button", name="Log in").click()
        print("[login] Clicked Log in")

        page.wait_for_load_state("networkidle")
        time.sleep(3)

        final_url = page.url
        print(f"[login] Final URL: {final_url}")

        success = "auth.sparx-learning.com" not in final_url

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
        print("Usage: python -m voboai.sparx_login <username> <password> <school>")
        sys.exit(1)

    result = login(sys.argv[1], sys.argv[2], sys.argv[3], headless=False)
    if result["success"]:
        print(f"LOGIN OK -> {result['url']}")
    else:
        print(f"LOGIN FAILED -> {result.get('url')}")
