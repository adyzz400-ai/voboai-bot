"""
VoboAi — main Discord bot.

Flow:
  /menu → Login embed (Sparx Science branding)
           [🔐 Login] → Login prompt embed → [🔐 Login] → Discord Modal
             School / Username / Password / Login Type
           On submit → bot DMs you live progress embeds (paginated, red bars)

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
# Health check server — keeps Render's port check happy.
# Runs in a background thread so it never blocks the bot.
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
# Login Modal — School / Username / Password / Login Type
# ------------------------------------------------------------------
class LoginModal(discord.ui.Modal, title="VoboAi Login"):
    school = discord.ui.TextInput(
        label="School",
        placeholder="e.g. St Mary's High School",
        required=True,
        max_length=100,
    )
    username = discord.ui.TextInput(
        label="Username",
        placeholder="e.g. 123456",
        required=True,
        max_length=50,
    )
    password = discord.ui.TextInput(
        label="Password",
        placeholder="Your Sparx password",
        required=True,
        max_length=100,
    )
    login_type = discord.ui.TextInput(
        label="Login Type",
        placeholder="Normal / Microsoft / Google",
        required=False,
        max_length=20,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Acknowledge + start the automation
        await interaction.followup.send(
            f"✅ Credentials received!\n"
            f"**School:** {self.school.value}\n"
            f"**Username:** {self.username.value}\n"
            f"**Login Type:** {self.login_type.value or 'Normal'}\n\n"
            f"🤖 Starting automation — I'll DM you live progress.",
            ephemeral=True,
        )

        # Start the background automation thread
        threading.Thread(
            target=self._run_automation,
            args=(interaction,),
            daemon=True,
        ).start()

    def _run_automation(self, interaction: discord.Interaction):
        """Runs in a background thread. Sends progress DMs to the user."""
        import asyncio

        try:
            # --- Simulated progress: send paginated progress embeds ---
            for page, page_tasks in enumerate(
                [
                    [("Task 1", 100), ("Task 2", 100), ("Task 3", 100)],
                    [("Task 4", 100), ("Task 5", 100), ("Task 6", 100)],
                ],
                start=1,
            ):
                embed = embeds.progress_embed(
                    page=page,
                    total_pages=2,
                    tasks=page_tasks,
                )
                asyncio.run_coroutine_threadsafe(
                    interaction.user.send(embed=embed),
                    bot.loop,
                ).result()
                time.sleep(2)

            # Final success
            asyncio.run_coroutine_threadsafe(
                interaction.user.send(embed=embeds.success_embed()),
                bot.loop,
            ).result()
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                interaction.user.send(f"❌ Automation error: {e}"),
                bot.loop,
            ).result()


# ------------------------------------------------------------------
# Views
# ------------------------------------------------------------------
class HomeView(discord.ui.View):
    """Buttons on the main login embed."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔐 Login", style=discord.ButtonStyle.red, row=0)
    async def go_login(self, interaction, button):
        await interaction.response.edit_message(
            embed=embeds.login_prompt_embed(), view=LoginPromptView()
        )

    @discord.ui.button(label="📚 Check Queue", style=discord.ButtonStyle.gray, row=0)
    async def go_queue(self, interaction, button):
        await interaction.response.send_message(
            embed=embeds.progress_embed(), ephemeral=True
        )


class LoginPromptView(discord.ui.View):
    """Buttons on the 'Login by entering your account details' embed."""
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


@bot.tree.command(name="menu", description="Open the VoboAi menu")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=embeds.login_embed(config.ACTIVE_SUBJECT), view=HomeView()
    )


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN not set. Add it to Render env vars.")

    threading.Thread(target=run_health_server, daemon=True).start()
    bot.run(config.DISCORD_TOKEN)
