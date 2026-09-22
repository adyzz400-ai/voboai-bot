"""
VoboAi — main Discord bot.

One slash command:  /menu
Buttons navigate between all screens (Menu / Login / Queue / Success).

Run:  python bot.py
"""
import discord
from discord import app_commands
from discord.ext import commands

import config
import embeds


class MenuView(discord.ui.View):
    """Button row that appears on every screen so users can navigate."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.blurple, row=0)
    async def home(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=embeds.menu_embed(), view=MenuView())

    @discord.ui.button(label="🔐 Login", style=discord.ButtonStyle.red, row=0)
    async def login(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=embeds.login_embed(), view=MenuView())

    @discord.ui.button(label="📚 Queue", style=discord.ButtonStyle.gray, row=0)
    async def queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=embeds.queue_embed(), view=MenuView())

    @discord.ui.button(label="✅ Success", style=discord.ButtonStyle.green, row=0)
    async def success(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=embeds.success_embed(), view=MenuView())


class VoboAiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Register the /menu command globally (works in every server).
        await self.tree.sync()
        print("Slash commands synced.")


bot = VoboAiBot()


@bot.event
async def on_ready():
    print(f"{config.BOT_NAME} is online as {bot.user} ({bot.user.id})")
    print(f"Version {config.BOT_VERSION} — {config.BOT_TAGLINE}")


@bot.tree.command(name="menu", description="Open the VoboAi menu with all screens")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(embed=embeds.menu_embed(), view=MenuView())


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN not set. Add it to your Render env vars.")
    bot.run(config.DISCORD_TOKEN)
