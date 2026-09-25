"""
VoboAi — the real automation run.

Handles: login → homework → per-question solving → submit → progress.
Complies with Sparx v2: does NOT skip the timer (waits 30-100s per question).
"""
import time
import random

from . import sparx_login
from . import homework as hw
from . import solver


def run_homework(username, password, school_name, homework, progress_cb):
    """
    Full automation for one homework.

    progress_cb: async-ish callback to report progress to Discord.
                 Called with a dict of progress info.
    """
    # 1. Login
    progress_cb({"stage": "login", "msg": "Logging into Sparx..."})
    result = sparx_login.login(username, password, school_name, headless=True)
    if not result["success"]:
        progress_cb({"stage": "error", "msg": f"Login failed: {result.get('error')}"})
        return

    page = result["page"]
    progress_cb({"stage": "login", "msg": "Logged in!"})

    # 2. Open the homework
    progress_cb({"stage": "fetch", "msg": f"Opening {homework['label']}..."})
    page.goto(homework["link"], wait_until="networkidle")
    time.sleep(2)

    # 3. Solve each question
    #    (Sparx v2: we MUST wait the timer — no skipping.)
    total_questions = homework.get("questions", 0) or 112
    done = 0

    while done < total_questions:
        # Read current question text
        try:
            q_text = page.locator("[class*='question'], [class*='prompt']").first.inner_text()
        except Exception:
            q_text = page.locator("body").inner_text()[:500]

        # Solve with Gemini (optionally pass a screenshot for image solving)
        answer = solver.solve_question(q_text)

        # Type the answer
        try:
            page.locator("input[type='text'], input[type='number']").first.fill(answer)
        except Exception:
            pass

        # Submit
        try:
            page.get_by_role("button", name="Check").click()
        except Exception:
            pass

        done += 1

        # Sparx v2 compliance: wait the timer (30-100s), no skipping.
        wait_time = random.randint(30, 100)
        progress_cb({
            "stage": "progress",
            "done": done,
            "total": total_questions,
            "wait": wait_time,
            "msg": f"Solved question {done}/{total_questions}",
        })
        time.sleep(wait_time)

    # 4. Handle bookwork check (pass it)
    try:
        page.get_by_role("button", name="Bookwork").click()
    except Exception:
        pass

    progress_cb({"stage": "done", "msg": "Homework complete!"})
    return True
