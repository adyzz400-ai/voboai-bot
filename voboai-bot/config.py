import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

BOT_NAME = "VoboAi"
BOT_VERSION = "1.2.0"
BOT_TAGLINE = "Sparx automation, zero detection"

# Active subject for the embeds (Science / Maths / Educake)
ACTIVE_SUBJECT = os.getenv("VOB_ACTIVE_SUBJECT", "Maths")

SUBJECTS = {
    "sparx_science": {"label": "Science", "home": "Sparx Science"},
    "sparx_maths": {"label": "Maths", "home": "Sparx Maths"},
    "educake": {"label": "Educake", "home": "Educake"},
}
