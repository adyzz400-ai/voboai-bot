"""
VoboAi — embed designs.

Login embed:  Sparx Science branding + features list + Login/Check Queue buttons.
Progress embed: per-homework task list with pagination, red progress bars.
"""
import discord


# ------------------------------------------------------------------
# Menu / login embed
# ------------------------------------------------------------------
def login_embed(subject: str = "Science") -> discord.Embed:
    e = discord.Embed(
        title=f"Sparx {subject}",
        description=(
            f"Automate your Sparx {subject} homework with high accuracy and "
            f"zero detection by your teacher. Simply press Login and follow the "
            f"instructions to be on your way to acing your Sparx {subject} "
            f"homework and never fearing of Sparx {subject} again in your life!"
        ),
        color=discord.Color.from_rgb(231, 76, 60),  # red accent
    )

    e.add_field(
        name="🪄 Features",
        value=(
            "**⏰ Customisable Time** — Autocompletes your homework in whatever "
            "time you want to balance speed and detection!\n"
            "**🎯 High Accuracy** — Excellent accuracy of >90% at completing questions!\n"
            "**🧠 Easy To Use** — Simple and intuitive to use with the press of "
            "only a few buttons!"
        ),
        inline=False,
    )

    # Footer branding
    e.set_footer(text=f"VoboAi • Sparx {subject} • Zero detection")
    return e


# ------------------------------------------------------------------
# Login prompt embed (after pressing Login)
# ------------------------------------------------------------------
def login_prompt_embed(subject: str = "Science") -> discord.Embed:
    e = discord.Embed(
        title="Login",
        description="Login by entering your account details! 🌟",
        color=discord.Color.from_rgb(231, 76, 60),
    )
    e.set_footer(text=f"VoboAi • Sparx {subject}")
    return e


# ------------------------------------------------------------------
# Progress embed — with pagination and red bars
# ------------------------------------------------------------------
def progress_embed(
    homework_name: str = "Homework due Wednesday 23rd Sept...",
    status: str = "Completed (112 questions)",
    page: int = 1,
    total_pages: int = 2,
    tasks: list = None,
    questions_done: int = 112,
    questions_total: int = 112,
    time_spent: str = "1h 7m",
    question_time: str = "30s - 100s",
    bookwork: str = "High",
    xp: int = 470,
    subject: str = "Science",
) -> discord.Embed:
    """Progress embed. `tasks` is a list of (label, percent) tuples for the page."""
    if tasks is None:
        tasks = [
            ("Task 1", 100),
            ("Task 2", 100),
            ("Task 3", 100),
            ("Task 4", 100),
            ("Task 5", 100),
            ("Task 6", 100),
        ]

    e = discord.Embed(
        title=f"📚 Sparx {subject} Progress",
        color=discord.Color.from_rgb(231, 76, 60),  # red theme
    )

    e.add_field(name="Name", value=homework_name, inline=False)

    # Status line
    e.add_field(name="Status", value=f"`{status}`", inline=False)

    # Page indicator
    e.add_field(name="Page", value=f"`{page} of {total_pages}`", inline=False)

    # Task list with red progress bars
    task_lines = []
    for i, (label, pct) in enumerate(tasks, 1):
        bar = _red_bar(pct)
        task_lines.append(f"{i}. **{label}** `{pct}%`\n{bar}")
    e.add_field(name="Tasks", value="\n".join(task_lines), inline=False)

    # Stats
    e.add_field(
        name="📊 Stats",
        value=(
            f"**Questions Completed:** {questions_done}/{questions_total}\n"
            f"**Time spent:** {time_spent}\n"
            f"**Question Time:** {question_time}\n"
            f"**Bookwork Accuracy:** {bookwork}\n"
            f"**XP Gained:** {xp}"
        ),
        inline=False,
    )

    e.add_field(
        name="📌 Note",
        value="Your school's on Sparx Maths v2 so we can't skip the timer anymore.",
        inline=False,
    )

    e.set_footer(text=f"VoboAi • Sparx {subject} • Page {page}/{total_pages}")
    return e


def _red_bar(pct: float, width: int = 12) -> str:
    """A red progress bar built from block characters."""
    filled = int(round(pct / 100 * width))
    filled = max(0, min(width, filled))
    bar = "█" * filled + "░" * (width - filled)
    # Red via inline code (renders as a clean block bar)
    return f"`{bar}`"


# ------------------------------------------------------------------
# Success embed
# ------------------------------------------------------------------
def success_embed(subject: str = "Science", xp: int = 470) -> discord.Embed:
    e = discord.Embed(
        title=f"✅ Sparx {subject} Complete!",
        description=(
            f"All homework finished with high accuracy.\n"
            f"**XP Gained:** {xp}\n"
            f"**Bookwork:** Passed ✅"
        ),
        color=discord.Color.from_rgb(46, 204, 113),  # green
    )
    e.set_footer(text="VoboAi • Zero detection")
    return e
