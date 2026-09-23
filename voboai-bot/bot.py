"""
VoboAi — main Discord bot.

One slash command:  /menu
Each screen is its OWN embed with ONLY the relevant navigation buttons.

Login uses a Discord Modal (popup form) that feeds the real Sparx
automation running in a background thread.

Run:  python bot.py
"""
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord import app_commands
from discord.ext import commands

import config
import embeds

# --- Automation (Playwright) ---
try:
    from voboai import sparx_login
    HAS_AUTOMATION = True
except Exception:
    HAS_AUTOMATION = False


# ------------------------------------------------------------------
# Health check server — lets Render's port check pass.
# Runs in a background thread so it NEVER blocks the bot.
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
# Login Modal — popup form with text boxes
# ------------------------------------------------------------------
class LoginModal(discord.ui.Modal, title="VoboAi Login"):
    username = discord.ui.TextInput(
        label="Sparx Username",
        placeholder="e.g. 123456",
        required=True,
        max_length=50,
    )
    password = discord.ui.TextInput(
        label="Sparx Password",
        placeholder="Your Sparx password",
        required=True,
        max_length=100,
    )
    school = discord.ui.TextInput(
        label="School Name",
        placeholder="e.g. St Mary's High School",
        required=True,
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"🔐 Logging you into **{self.school.value}**...",
            ephemeral=True,
        )

        # Run the real Sparx login in a background thread.
        if HAS_AUTOMATION:
            def worker():
                try:
                    result = sparx_login.login(
                        self.username.value,
                        self.password.value,
                        self.school.value,
                        headless=True,
                    )
                    if result["success"]:
                        # TODO: fetch homework, then AI solve
                        msg = f"✅ Logged in! Final URL: {result['url']}"
                    else:
                        msg = f"❌ Login failed: {result.get('error', 'unknown')}"
                except Exception as e:
                    msg = f"❌ Error: {e}"

                # Post result back to Discord from the worker thread.
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    interaction.followup.send(msg, ephemeral=True),
                    bot.loop,
                )

            threading.Thread(target=worker, daemon=True).start()
        else:
            await interaction.followup.send(
                "⚠️ Automation module not installed. Install Playwright + "
                "`pip install playwright && playwright install chromium`.",
                ephemeral=True,
            )


# ------------------------------------------------------------------
# Views — each screen has its own button set.
# ------------------------------------------------------------------
class HomeView(discord.ui.View):
    """Buttons on the Menu embed."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔐 Login", style=discord.ButtonStyle.red, row=0)
    async def go_login(self, interaction, button):
        await interaction.response.send_modal(LoginModal())

    @discord.ui.button(label="📚 Queue", style=discord.ButtonStyle.gray, row=0)
    async def go_queue(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.queue_embed(), view=QueueView())

    @discord.ui.button(label="✅ Success", style=discord.ButtonStyle.green, row=0)
    async def go_success(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.success_embed(), view=SuccessView())


class QueueView(discord.ui.View):
    """Buttons on the Queue embed."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.blurple, row=0)
    async def go_home(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.menu_embed(), view=HomeView())


class SuccessView(discord.ui.View):
    """Buttons on the Success embed."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.blurple, row=0)
    async def go_home(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.menu_embed(), view=HomeView())


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


@bot.tree.command(name="menu", description="Open the VoboAi menu")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(embed=embeds.menu_embed(), view=HomeView())


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN not set. Add it to Render env vars.")

    # Health server in a background thread — keeps Render's port check happy
    # WITHOUT blocking the bot from starting.
    threading.Thread(target=run_health_server, daemon=True).start()

    # Main thread runs the bot — this is what brings it online.
    bot.run(config.DISCORD_TOKEN)
