"""
VoboAi — embed builders. One source of truth for every screen.
"""
import discord
import config


def _footer(embed: discord.Embed):
    embed.set_footer(text=f"{config.BOT_NAME} v{config.BOT_VERSION} • {config.BOT_TAGLINE}")
    return embed


def menu_embed() -> discord.Embed:
    e = discord.Embed(
        title="🏠 VoboAi — Home",
        description="Your **Sparx Maths** & **Educake** autocompleter.\nUse the buttons below to navigate.",
        color=config.COLOR_BRAND,
    )
    e.add_field(name="📊 Live Stats", value="```\n0  online\n0  solving\n0  in queue\n```", inline=True)
    e.add_field(name="⚡ Quick Start", value="1. **Login**\n2. **Homework**\n3. Watch progress", inline=True)
    e.add_field(name="🛠 Subjects", value="• **Sparx Maths** — ready\n• **Educake** — coming soon", inline=False)
    e.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/1.png")
    _footer(e)
    return e


def login_embed(subject: str = "sparx") -> discord.Embed:
    name = config.SUBJECTS.get(subject, subject.title())
    e = discord.Embed(
        title=f"🔐 Link your {name} account",
        description="Press **Login** to open a form and enter your school, username and password.",
        color=config.COLOR_LOGIN,
    )
    e.add_field(name="🏫 School", value="*Not set yet*", inline=True)
    e.add_field(name="👤 User", value="*Not set yet*", inline=True)
    e.add_field(name="🔑 Password", value="`••••••••`", inline=True)
    e.add_field(name="ℹ️ Note", value="Credentials are used only for your own account.", inline=False)
    _footer(e)
    return e


def queue_embed(subject: str = "sparx", progress: float = 0.0) -> discord.Embed:
    name = config.SUBJECTS.get(subject, subject.title())
    pct = max(0.0, min(100.0, progress))
    bar_len = 12
    filled = round(pct / 100 * bar_len)
    bar = "🟩" * filled + "⬛" * (bar_len - filled)
    e = discord.Embed(
        title=f"📚 {name} — Task Queue",
        description=f"**Overall progress:** {pct:.0f}%\n{bar}",
        color=config.COLOR_QUEUE,
    )
    e.add_field(name="⏳ Pending", value="`0`", inline=True)
    e.add_field(name="⚙️ In progress", value="`0`", inline=True)
    e.add_field(name="✅ Completed", value="`0`", inline=True)
    e.add_field(name="🧾 Current task", value="*Nothing running yet. Select a task to begin.*", inline=False)
    _footer(e)
    return e


def success_embed(subject: str = "sparx", task: str = "Example task",
                  answer: str = "42", elapsed: float = 12.5, confidence: float = 0.95) -> discord.Embed:
    name = config.SUBJECTS.get(subject, subject.title())
    e = discord.Embed(
        title=f"✅ Task Solved — {name}",
        description=f"**{task}**",
        color=config.COLOR_SUCCESS,
    )
    e.add_field(name="📝 Answer", value=f"```{answer}```", inline=True)
    e.add_field(name="⏱ Time taken", value=f"`{elapsed:.1f}s`", inline=True)
    e.add_field(name="🎯 Confidence", value=f"`{confidence * 100:.0f}%`", inline=True)
    e.add_field(name="🏆 Rewards", value="+**10 XP**  •  🔥 streak +1", inline=False)
    _footer(e)
    return e


def status_embed(title: str, description: str, color: int = config.COLOR_BRAND) -> discord.Embed:
    e = discord.Embed(title=title, description=description, color=color)
    _footer(e)
    return e


def login_status_embed(state: str, subject: str = "sparx", **kw) -> discord.Embed:
    """Enhanced login status messages (requirement #7)."""
    if state == "attempting":
        return status_embed("🟡 Attempting to login…",
                            f"Connecting to **{config.SUBJECTS.get(subject)}** as `{kw.get('user','?')}`…",
                            config.COLOR_QUEUE)
    if state == "school":
        return status_embed("🏫 School found",
                            f"Found **{kw.get('school','?')}** ({kw.get('town','?')}) — selecting…",
                            config.COLOR_QUEUE)
    if state == "filling":
        return status_embed("✍️ Filling login form…", "Entering your credentials…", config.COLOR_QUEUE)
    if state == "submitting":
        return status_embed("🔐 Submitting credentials…", "Logging you in…", config.COLOR_QUEUE)
    if state == "sso":
        return status_embed("🔵 Redirecting to SSO…",
                            "Taking you to your school's Microsoft/Google sign-in.", config.COLOR_BRAND)
    if state == "success":
        return status_embed("✅ Logged in!",
                            f"Welcome back, `{kw.get('user','?')}`. Fetching your homework…",
                            config.COLOR_SUCCESS)
    if state == "failure":
        return status_embed("❌ Unable to login",
                            "**Account not found** or wrong password. Please try again.", config.COLOR_ERROR)
    return status_embed("Login", f"Unknown state: {state}")
