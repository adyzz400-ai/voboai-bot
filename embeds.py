"""
VoboAi — embed designs.

Login embed:   Sparx Maths branding + features.
Select embed:  dropdown to pick which real homework to run.
Progress embed: per-task list with PNG progress bars (attached as files).
"""
import discord


# ------------------------------------------------------------------
# Login embed (Sparx Maths branding)
# ------------------------------------------------------------------
def login_embed() -> discord.Embed:
    e = discord.Embed(
        title="Sparx Maths",
        description=(
            "Automate your Sparx Maths homework with high accuracy and "
            "zero detection by your teacher. Simply press Login and follow the "
            "instructions to be on your way to acing your Sparx Maths "
            "homework and never fearing of Sparx Maths again in your life!"
        ),
        color=discord.Color.from_rgb(231, 76, 60),
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
    e.set_footer(text="VoboAi • Sparx Maths • Zero detection")
    return e


# ------------------------------------------------------------------
# Login prompt embed
# ------------------------------------------------------------------
def login_prompt_embed() -> discord.Embed:
    e = discord.Embed(
        title="Login",
        description="Login by entering your account details! 🌟",
        color=discord.Color.from_rgb(231, 76, 60),
    )
    e.set_footer(text="VoboAi • Sparx Maths")
    return e


# ------------------------------------------------------------------
# Select homework embed (with dropdown)
#   tasks: list of dicts {label, due, questions, link}
# ------------------------------------------------------------------
def select_embed(tasks: list) -> discord.Embed:
    e = discord.Embed(
        title="📚 Select Homework",
        description="Choose which homework you want VoboAi to complete:",
        color=discord.Color.from_rgb(231, 76, 60),
    )
    for i, t in enumerate(tasks[:25], 1):
        label = t.get("label") or f"Homework {i}"
        due = t.get("due", "?")
        q = t.get("questions", 0)
        e.add_field(name=f"{i}. {label}", value=f"Due: {due} • {q} questions", inline=False)
    e.set_footer(text="VoboAi • Sparx Maths")
    return e


# ------------------------------------------------------------------
# Progress embed — uses PNG progress bars (attached as files)
# ------------------------------------------------------------------
def progress_embed(
    homework_name: str,
    status: str,
    page: int,
    total_pages: int,
    tasks: list,          # list of (label, pct)
    questions_done: int,
    questions_total: int,
    time_spent: str,
    question_time: str,
    bookwork: str,
    xp: int,
) -> discord.Embed:
    e = discord.Embed(
        title="📚 Sparx Maths Progress",
        color=discord.Color.from_rgb(231, 76, 60),
    )
    e.add_field(name="Name", value=homework_name, inline=False)
    e.add_field(name="Status", value=f"`{status}`", inline=False)
    e.add_field(name="Page", value=f"`{page} of {total_pages}`", inline=False)

    # Task list with PNG bars (bars attached as files when message is sent)
    task_lines = []
    for i, (label, pct) in enumerate(tasks, 1):
        task_lines.append(f"{i}. **{label}** `{pct}%`")
    e.add_field(name="Tasks", value="\n".join(task_lines) or "—", inline=False)

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
    e.set_footer(text=f"VoboAi • Sparx Maths • Page {page}/{total_pages}")
    return e


# ------------------------------------------------------------------
# Success embed
# ------------------------------------------------------------------
def success_embed(xp: int = 470) -> discord.Embed:
    e = discord.Embed(
        title="✅ Sparx Maths Complete!",
        description=(
            f"All homework finished with high accuracy.\n"
            f"**XP Gained:** {xp}\n"
            f"**Bookwork:** Passed ✅"
        ),
        color=discord.Color.from_rgb(46, 204, 113),
    )
    e.set_footer(text="VoboAi • Zero detection")
    return e
