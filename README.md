# VoboAi — Discord autocompleter

Sparx Maths & Educake autocompleter bot. One command: `/menu`.

## Deploy on Render (from iOS)
1. Create a GitHub repo and upload these files.
2. Go to render.com → New → Web Service → connect your GitHub repo.
3. Runtime: **Python**. Build: `pip install -r requirements.txt`. Start: `python bot.py`.
4. Add env vars: `DISCORD_TOKEN` and `GUILD_IDS`.
5. Deploy. Invite the bot to your server, then run `/menu`.

## Commands
- `/menu` — open the menu with navigation buttons (Home / Login / Queue / Success)

## Roadmap
- [x] `/menu` + navigation buttons
- [ ] Real Sparx login (Playwright)
- [ ] Fetch real homework + dropdown
- [ ] AI solving (Gemini) + Cloudflare bypass
- [ ] Real-time progress
- [ ] Educake support
