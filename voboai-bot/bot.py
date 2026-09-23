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
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord import app_commands
from discord.ext import commands

import config
import embeds


# ------------------------------------------------------------------
# Health check server — lets Render's port check pass.
# (Not needed if you use a Background Worker instead of Web Service.)
# ------------------------------------------------------------------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"VoboAi is running")

    def log_message(self, *args):
        pass


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


@bot.tree.command(name="menu", description="Open the VoboAi menu")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(embed=embeds.menu_embed(), view=HomeView())


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN not set. Add it to Render env vars.")

    # Start the health server so Render sees an open port.
    # Remove this block if you switched to a Background Worker.
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()
    bot.run(config.DISCORD_TOKEN)
