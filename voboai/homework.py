"""
VoboAi — scrape the Sparx homework list after login.
"""
import time


def fetch_homework(page):
    """
    Given an authenticated Playwright page (already logged in), navigate to
    the homework page and extract the list of homework tasks.

    Returns a list of dicts:
        {label, due, questions, link}
    """
    from config import HOMEWORK_URL

    page.goto(HOMEWORK_URL, wait_until="networkidle")
    time.sleep(2)

    tasks = []

    # Sparx homework cards usually have a title and a due date.
    # Selectors may need adjustment on first live run.
    cards = page.locator("[class*='homework'], [class*='card'], [class*='task']")
    count = cards.count()
    for i in range(count):
        card = cards.nth(i)
        try:
            label = card.inner_text().splitlines()[0].strip()
        except Exception:
            label = f"Homework {i+1}"
        tasks.append({
            "label": label,
            "due": "See Sparx",
            "questions": 0,
            "link": HOMEWORK_URL,
        })

    if not tasks:
        # Fallback: grab visible text as a raw list
        tasks = [{"label": t, "due": "?", "questions": 0, "link": HOMEWORK_URL}
                 for t in page.locator("body").inner_text().splitlines() if t.strip()]

    return tasks
