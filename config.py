import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# Your Gemini API key — put it here or better, as a Render env var
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6I4nZDvNNDcvy0btaFp30o-FRggR-gR3dnrFHiA7llGRhg")

# Sparx homework page
HOMEWORK_URL = "https://maths.sparx-learning.com/student/homework?pkg_type=homework"

BOT_NAME = "VoboAi"
BOT_VERSION = "2.0.0"
BOT_TAGLINE = "Sparx Maths automation, zero detection"

# Timing — minimum 30 minutes per run, question time 30-100s
MIN_RUN_SECONDS = 30 * 60
QUESTION_TIME_MIN = 30
QUESTION_TIME_MAX = 100
