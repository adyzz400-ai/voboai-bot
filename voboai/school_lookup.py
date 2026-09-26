"""
VoboAi — Sparx school lookup.

Loads the full Sparx school list from the bundled data file and finds a
school by name.

School entry fields:
    u : slug (short code)
    i : UUID (unique school id)
    n : school name
    t : town
    a : address
    p : list of products/subjects
"""
import base64
import json
import os
import re
import unicodedata

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sparx-schools.txt")

_DIACRITICS = re.compile(r"[\u0300-\u036f]")
_L_STROKE = re.compile(r"ł")
_N_TILDE = re.compile(r"ñ")


def _normalize(text: str) -> str:
    return (
        _DIACRITICS.sub("", unicodedata.normalize("NFD", _L_STROKE.sub("l", _N_TILDE.sub("n", text))))
        .lower()
        .strip()
    )


def _load_schools():
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        return json.loads(base64.b64decode(f.read()))


def find_school(name: str, schools=None):
    if schools is None:
        schools = _load_schools()
    q = _normalize(name)
    if not q:
        return None

    best = None
    best_score = float("inf")
    for s in schools:
        n = _normalize(s.get("n", ""))
        if not n:
            continue
        if n == q:
            return s
        if n.startswith(q):
            score = 1
        elif q in n:
            score = 2
        else:
            score = 3
        if score < best_score:
            best_score = score
            best = s
    return best


def search_schools(name: str, limit: int = 10, schools=None):
    if schools is None:
        schools = _load_schools()
    q = _normalize(name)
    if not q:
        return []

    scored = []
    for s in schools:
        n = _normalize(s.get("n", ""))
        if not n:
            continue
        if n == q:
            score = 0
        elif n.startswith(q):
            score = 1
        elif q in n:
            score = 2
        else:
            continue
        scored.append((score, s))
    scored.sort(key=lambda x: (x[0], x[1]["n"].lower()))
    return [s for _, s in scored[:limit]]


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "Dunottar"
    print(f"Searching for: {query!r}")
    for s in search_schools(query):
        print(f"  {s['n']}  (slug={s['u']}, id={s['i']})")
