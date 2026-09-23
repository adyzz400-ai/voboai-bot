"""
VoboAi — main Discord bot.

One slash command:  /menu
Each screen is its OWN embed with ONLY the relevant navigation buttons.

Flow:
  /menu → Menu embed
            [🔐 Login] [📚 Queue] [✅ Success]
              │           │           │
              ▼           ▼           ▼
          Login       Queue       Success
              └─────── [🏠 Home] back ───────┘

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
# Views — each screen has its own button set.
# ------------------------------------------------------------------
class HomeView(discord.ui.View):
    """Buttons on the Menu embed."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔐 Login", style=discord.ButtonStyle.red, row=0)
    async def go_login(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.login_embed(), view=LoginView())

    @discord.ui.button(label="📚 Queue", style=discord.ButtonStyle.gray, row=0)
    async def go_queue(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.queue_embed(), view=QueueView())

    @discord.ui.button(label="✅ Success", style=discord.ButtonStyle.green, row=0)
    async def go_success(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.success_embed(), view=SuccessView())


class LoginView(discord.ui.View):
    """Buttons on the Login embed."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.blurple, row=0)
    async def go_home(self, interaction, button):
        await interaction.response.edit_message(embed=embeds.menu_embed(), view=HomeView())

    @discord.ui.button(label="✅ Done", style=discord.ButtonStyle.green, row=0)
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
    # Force the bot to appear online by setting presence.
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
