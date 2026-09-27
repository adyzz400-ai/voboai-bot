import json
import os
import subprocess

from playwright.sync_api import sync_playwright


WORKER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "sparx",
        "worker.js",
    )
)


def login(
    username,
    password,
    school_name,
    headless=True,
):
    playwright = None
    browser = None

    try:
        request = {
            "username": username,
            "password": password,
            "school": school_name,
        }

        result = subprocess.run(
            [
                "node",
                WORKER,
            ],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            timeout=120,
        )

        output = result.stdout.strip()

        if not output:
            return {
                "success": False,
                "error": (
                    result.stderr.strip()
                    or "Sparx worker returned no output."
                ),
            }

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": (
                    "Sparx worker returned invalid JSON: "
                    + output[:500]
                ),
            }

        if not data.get("success"):
            return {
                "success": False,
                "error": data.get(
                    "error",
                    "Sparx login failed.",
                ),
            }

        storage_state = data.get("storage_state")

        if not storage_state:
            return {
                "success": False,
                "error": "Sparx login returned no session.",
            }

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
            storage_state=storage_state,
            viewport={
                "width": 1280,
                "height": 900,
            },
        )

        page = context.new_page()

        return {
            "success": True,
            "page": page,
            "browser": browser,
            "context": context,
            "playwright": playwright,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": (
                "Sparx login timed out "
                "after 120 seconds."
            ),
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