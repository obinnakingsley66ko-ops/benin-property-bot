# Benin City Real Estate Telegram Bot

Automated property listing bot for Benin City, Edo State, Nigeria.

Scrapes live listings from **Nigeria Property Centre**, sends full private details to the admin, and posts clean attractive listings (with photos) to a public Telegram channel — every 2 hours automatically.

---

## How It Works

| Who sees what | Content |
|---|---|
| **Admin** (@Kingsley0136) | Title · Location · Price · Phone · Direct link |
| **Public channel** (@beninpropertyhub) | Title · Location · Photo · Selling points · DM call-to-action |

Admin acts as middleman — channel followers DM the admin for price and inspection.

---

## Quick Start (Termux / Android)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/obinnakingsley66ko-ops/benin-property-bot.git
cd benin-property-bot
pip install -r requirements.txt
python main.py
```

---

## Full Termux Setup

See [TERMUX_SETUP.md](TERMUX_SETUP.md) for a complete step-by-step guide including `.env` configuration, `tmux` persistence, and troubleshooting.

---

## Configuration (`.env` file)

```bash
cp .env.example .env
nano .env
```

| Variable | Description |
|---|---|
| `BOT_TOKEN` | From @BotFather on Telegram |
| `ADMIN_CHAT_ID` | Your chat ID — use @userinfobot |
| `CHANNEL_ID` | `@beninpropertyhub` or numeric ID |

---

## File Structure

```
telegram-bot/
├── main.py           — Entry point and main scheduler loop
├── config.py         — All settings; reads from .env automatically
├── scraper.py        — Scrapes nigeriapropertycentre.com (multi-page)
├── filter.py         — Quality gate: phone, image, price, Benin keyword
├── caption.py        — Dynamic channel captions with selling points
├── telegram_bot.py   — All Telegram API calls (sendMessage, sendPhoto)
├── storage.py        — posted.json read/write; duplicate tracking
├── .env.example      — Template — copy to .env and fill in values
├── run.sh            — One-click launcher with dependency check
├── requirements.txt  — Python dependencies
└── TERMUX_SETUP.md   — Full Termux deployment guide
```

---

## Bot Commands

| Command | Response |
|---|---|
| `/start` | Welcome message |
| `/listings` | How to browse properties |
| `/contact` | How to reach the admin |
| `/help` | All available commands |

---

## Filters Applied Each Run

- Title, price, phone, image, and listing URL must all be present
- Price must be ≤ ₦20,000,000 per annum (filters extreme luxury outliers)
- Location must reference Benin City / Edo State
- URL must not already be in `posted.json` (no duplicates)
- Residential listings are sorted before office/commercial
- Maximum 5 listings sent per 2-hour cycle

---

## Data Source

**Nigeria Property Centre** — `nigeriapropertycentre.com/for-rent/edo/benin-city`

This site does not require JavaScript and is accessible without Cloudflare bypass.

---

## Deploying on Replit

1. Add secrets via Replit Secrets: `BOT_TOKEN`, `ADMIN_CHAT_ID`, `CHANNEL_ID`
2. Set the workflow command to: `python3 telegram-bot/main.py`
3. The bot starts automatically and runs every 2 hours

---

## Important

Make sure your bot (`@beninpropertybot`) is added as **Admin** with **Post Messages** permission in your channel before running.
