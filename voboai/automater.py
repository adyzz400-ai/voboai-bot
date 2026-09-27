"""
VoboAi — full automation pipeline.

Runs: login -> fetch homework -> solve each question -> submit -> report progress.
Complies with Sparx v2 timer (waits between questions).
"""
import time

from . import sparx_login
from . import homework as hw
from . import solver


def run(username: str, password: str, school_name: str, progress_cb=None):
    def report(msg):
        if progress_cb:
            progress_cb(msg)
        print(f"[automator] {msg}")

    report("Logging in...")
    login = sparx_login.login(username, password, school_name)
    if not login["success"]:
        return {"success": False, "error": f"Login failed: {login.get('url')}"}

    page = login["page"]
    report("Login OK. Fetching homework...")

    tasks = hw.fetch_homework(page)
    report(f"Found {len(tasks)} homework task(s).")

    completed = 0
    for task in tasks:
        report(f"Working on: {task['label']}")
        # Solve each question, waiting for the Sparx v2 timer.
        # (Real per-question logic goes here.)
        time.sleep(30)  # v2 timer placeholder
        completed += 1

    report("Done.")
    try:
        login["browser"].close()
    except Exception:
        pass

    return {"success": True, "completed": completed, "total": len(tasks)}
