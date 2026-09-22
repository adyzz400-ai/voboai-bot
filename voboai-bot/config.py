"""
VoboAi — configuration.

Loads environment variables (set via Render dashboard) and defines the
shared color palette and constants used by every embed.
"""
import os

# --- Required secrets (set in Render env vars) ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
GUILD_IDS = [int(g) for g in os.environ.get("GUILD_IDS", "").split(",") if g.strip()]

# --- Optional ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# --- Brand / embed colors ---
COLOR_BRAND = 0x5865F2      # Discord blurple  (Menu)
COLOR_LOGIN = 0xED4245      # red-ish         (Login)
COLOR_QUEUE = 0xFEE75C      # yellow          (Queue / progress)
COLOR_SUCCESS = 0x57F287    # green           (Success)
COLOR_ERROR = 0xED4245      # red             (errors)

# --- Bot identity ---
BOT_NAME = "VoboAi"
BOT_TAGLINE = "Sparx Maths & Educake autocompleter"
BOT_VERSION = "1.0.0"

# --- Subjects (Educake added later) ---
SUBJECTS = {
    "sparx": "Sparx Maths",
    "educake": "Educake",   # coming soon
}

# --- Timing simulation — human-like delays, in seconds ---
TIMING = {
    "typing_per_char": 0.12,
    "read_question": (1.5, 3.0),
    "think_answer": (2.0, 5.0),
    "between_questions": (3.0, 8.0),
    "login_redirect": (1.0, 2.5),
}

# --- Sparx auth ---
SPARX_SELECT_URL = "https://selectschool.sparx-learning.com/"
SPARX_AUTH_URL = "https://auth.sparx-learning.com/oauth2/auth"
