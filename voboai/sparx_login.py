"""
VoboAi — Sparx Maths login automation.

Two-step login:
  1. School selection  -> done locally from the bundled school list
  2. Auth page         -> fill username/password, click "Log in"
"""
import time

from playwright.sync_api import sync_playwright

from .school_lookup import find_school


def _school_to_auth_url(school: dict) -> str:
    slug = school["u"]
    return f"https://{slug}.sparx-learning.com/oauth2/auth"


def login(username: str, password: str, school_name: str, headless: bool = True):
    school = find_school(school_name)
    if school is None:
        return {"success": False, "error": f"School not found: {school_name!r}"}

    print(f"[login] School matched: {school['n']} (slug={school['u']})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        auth_url = _school_to_auth_url(school)
        print(f"[login] Opening auth page: {auth_url}")
        page.goto(auth_url, wait_until="networkidle")

        page.fill("#username", username)
        print("[login] Filled username")

        page.fill("#password", password)
        print("[login] Filled password")

        try:
            page.get_by_role("button", name="Log in").click()
        except Exception:
            page.locator("button[type='submit']").click()
        print("[login] Clicked Log in")

        page.wait_for_load_state("networkidle")
        time.sleep(2)

        final_url = page.url
        print(f"[login] Final URL: {final_url}")

        success = "auth.sparx-learning.com" not in final_url

        return {
            "success": success,
            "page": page,
            "browser": browser,
            "context": context,
            "school": school,
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
        print(f"LOGIN FAILED -> {result.get('error', result.get('url'))}")
