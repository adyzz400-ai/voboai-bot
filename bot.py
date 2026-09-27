"""
VoboAi — main Discord bot (real automation).

Flow:
  /menu → Sparx Maths login embed
  [🔐 Login] → modal (School/Username/Password/Login Type)
  Submit → real Sparx login → scrape homework → DM "Select Homework" dropdown
  [pick task] → real automation runs (Gemini solves, waits timer, passes bookwork)
              → live progress DMs with PNG bars

Run:  python bot.py
"""
import os
import io
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord import app_commands
from discord.ext import commands

import config
import embeds
import os
import subprocess
import sys

# Ensure Playwright browser is installed (idempotent, fast if already there)
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/render/.cache/ms-playwright")
try:
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True,
        capture_output=True,
    )
except subprocess.CalledProcessError as e:
    print("[startup] Playwright install failed:", e.stderr.decode())

from voboai import sparx_login, homework as hw, automator


# ------------------------------------------------------------------
# Health check server
# ------------------------------------------------------------------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"VoboAi is running")

    def log_message(self, *args):
        pass


def run_health_server():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()


# ------------------------------------------------------------------
# Progress bar PNG files
# ------------------------------------------------------------------
BAR_FILES = {}
def load_bars():
    import pathlib
    for pct in [0, 25, 50, 75, 100]:
        p = pathlib.Path(f"bars/bar_{pct}.png")
        if p.exists():
            BAR_FILES[pct] = discord.File(p, filename=f"bar_{pct}.png")


# ------------------------------------------------------------------
# Login Modal
# ------------------------------------------------------------------
class LoginModal(discord.ui.Modal, title="VoboAi Login"):
    school = discord.ui.TextInput(label="School", placeholder="e.g. St Mary's High School", required=True, max_length=100)
    username = discord.ui.TextInput(label="Username", placeholder="e.g. 123456", required=True, max_length=50)
    password = discord.ui.TextInput(label="Password", placeholder="Your Sparx password", required=True, max_length=100)
    login_type = discord.ui.TextInput(label="Login Type", placeholder="Normal / Microsoft / Google", required=False, max_length=20)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"✅ Credentials received!\n**School:** {self.school.value}\n"
            f"**Username:** {self.username.value}\n\n"
            f"🔐 Logging into Sparx and fetching your homework...",
            ephemeral=True,
        )

        # Store credentials for the automation run
        self._creds = {
            "username": self.username.value,
            "password": self.password.value,
            "school": self.school.value,
        }

        # Run login + homework fetch in a background thread
        threading.Thread(
            target=self._fetch_and_show_homework,
            args=(interaction,),
            daemon=True,
        ).start()

    def _fetch_and_show_homework(self, interaction):
        import asyncio
        try:
            # Real login
            result = sparx_login.login(
                self._creds["username"],
                self._creds["password"],
                self._creds["school"],
                headless=True,
            )
            if not result["success"]:
                asyncio.run_coroutine_threadsafe(
                    interaction.followup.send(
                        f"❌ Login failed: {result.get('error', 'unknown')}",
                        ephemeral=True,
                    ), bot.loop).result()
                return

            page = result["page"]
            # Scrape real homework
            tasks = hw.fetch_homework(page)
            if not tasks:
                tasks = [{"label": "Homework", "due": "?", "questions": 0,
                          "link": config.HOMEWORK_URL}]

            # DM the select-homework dropdown with REAL tasks
            view = HomeworkSelectView(tasks, self._creds)
            asyncio.run_coroutine_threadsafe(
                interaction.user.send(
                    embed=embeds.select_embed(tasks), view=view
                ), bot.loop).result()
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                interaction.followup.send(f"❌ Error: {e}", ephemeral=True),
                bot.loop).result()


# ------------------------------------------------------------------
# Homework select dropdown (REAL homework)
# ------------------------------------------------------------------
class HomeworkSelect(discord.ui.Select):
    def __init__(self, tasks):
        options = []
        for i, t in enumerate(tasks[:25]):  # max 25 options
            options.append(discord.SelectOption(
                label=t["label"][:100] or f"Homework {i+1}",
                description=f"Due {t.get('due','?')} • {t.get('questions',0)} questions",
            ))
        super().__init__(placeholder="Choose a homework...", options=options)
        self.tasks = tasks

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        task = next((t for t in self.tasks if t["label"][:100] == choice), self.tasks[0])
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"🚀 Starting **{choice}**...\nI'll DM you live progress.\n"
            f"⏱️ This will take ~30min-1hr (Sparx v2 timer).",
            ephemeral=True,
        )
        threading.Thread(
            target=run_real_automation,
            args=(interaction.user, task, self._creds),
            daemon=True,
        ).start()


class HomeworkSelectView(discord.ui.View):
    def __init__(self, tasks, creds):
        super().__init__(timeout=600)
        self._creds = creds
        self.add_item(HomeworkSelect(tasks))


# ------------------------------------------------------------------
# Real automation runner
# ------------------------------------------------------------------
def run_real_automation(user, task, creds):
    """Runs the real Sparx automation and DMs live progress."""
    import asyncio
    import random

    start = time.time()
    total = task.get("questions", 0) or 112
    done = 0

    def progress_cb(info):
        nonlocal done
        stage = info.get("stage")
        if stage == "progress":
            done = info["done"]
            # Send a progress embed every question (or throttle)
            pct = int(done / total * 100)
            nearest = min([0,25,50,75,100], key=lambda p: abs(p-pct))
            embed = embeds.progress_embed(
                homework_name=task["label"],
                status=f"Running ({done}/{total} questions)",
                page=1,
                total_pages=1,
                tasks=[("Current task", pct)],
                questions_done=done,
                questions_total=total,
                time_spent=_fmt_time(time.time() - start),
                question_time=f"{config.QUESTION_TIME_MIN}s - {config.QUESTION_TIME_MAX}s",
                bookwork="Pending",
                xp=0,
            )
            files = [BAR_FILES[nearest]] if nearest in BAR_FILES else []
            asyncio.run_coroutine_threadsafe(
                user.send(embed=embed, files=files), bot.loop
            ).result()
        elif stage == "error":
            asyncio.run_coroutine_threadsafe(
                user.send(f"❌ {info['msg']}"), bot.loop
            ).result()
        elif stage == "done":
            embed = embeds.success_embed(xp=random.randint(300, 600))
            asyncio.run_coroutine_threadsafe(
                user.send(embed=embed), bot.loop
            ).result()

    try:
        automator.run_homework(
            creds["username"], creds["password"], creds["school"],
            task, progress_cb,
        )
    except Exception as e:
        asyncio.run_coroutine_threadsafe(
            user.send(f"❌ Automation error: {e}"), bot.loop
        ).result()


def _fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m"
    return f"{m}m {s}s"


# ------------------------------------------------------------------
# Views
# ------------------------------------------------------------------
class HomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔐 Login", style=discord.ButtonStyle.red, row=0)
    async def go_login(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.login_prompt_embed(), view=LoginPromptView())

    @discord.ui.button(label="📚 Check Queue", style=discord.ButtonStyle.gray, row=0)
    async def go_queue(self, interaction, button):
        await interaction.response.send_message("Queue is empty right now.", ephemeral=True)


class LoginPromptView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔐 Login", style=discord.ButtonStyle.red, row=0)
    async def open_modal(self, interaction, button):
        await interaction.response.send_modal(LoginModal())


# ------------------------------------------------------------------
# Bot
# ------------------------------------------------------------------
class VoboAiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")


bot = VoboAiBot()


@bot.event
async def on_ready():
    print(f"{config.BOT_NAME} is online as {bot.user} ({bot.user.id})")
    print(f"Version {config.BOT_VERSION} — {config.BOT_TAGLINE}")
    await bot.change_presence(status=discord.Status.online)
    load_bars()


@bot.tree.command(name="menu", description="Open the VoboAi menu")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(embed=embeds.login_embed(), view=HomeView())


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN not set. Add it to Render env vars.")
    threading.Thread(target=run_health_server, daemon=True).start()
    bot.run(config.DISCORD_TOKEN)
