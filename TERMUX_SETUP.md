# Running the Bot on Termux (Android)

This guide lets you run the Benin City Real Estate Bot on any Android phone using Termux — no laptop needed.

---

## Step 1 — Install Termux

Download **Termux** from F-Droid (recommended) or Google Play:
- https://f-droid.org/en/packages/com.termux/

---

## Step 2 — Set up Termux

Open Termux and run these commands one by one:

```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install --upgrade pip
```

---

## Step 3 — Clone the project from GitHub

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/benin-real-estate-bot.git
cd benin-real-estate-bot/telegram-bot
```

---

## Step 4 — Create your `.env` file

```bash
cp .env.example .env
nano .env
```

Fill in your values (use arrow keys to navigate, Ctrl+O to save, Ctrl+X to exit):

```
BOT_TOKEN=8636461678:AAFEjXWFtBo9N0Y1m_SNFBDXgzWW8a5wT54
ADMIN_CHAT_ID=7454290789
CHANNEL_ID=@beninpropertyhub
```

---

## Step 5 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Step 6 — Run the bot

```bash
bash run.sh
```

Or directly:

```bash
python3 main.py
```

---

## Keep it running when Termux is in background

Install `termux-wake-lock` to prevent Android from killing the process:

```bash
termux-wake-lock
python3 main.py
```

Or use **tmux** to keep the session alive:

```bash
pkg install tmux -y
tmux new -s bot
python3 main.py
# Press Ctrl+B then D to detach
# tmux attach -t bot     ← to return later
```

---

## Updating the bot

Pull the latest code from GitHub:

```bash
cd benin-real-estate-bot
git pull
cd telegram-bot
python3 main.py
```

---

## What the bot does

| What | Detail |
|------|--------|
| Scrapes from | nigeriapropertycentre.com — Benin City listings |
| Runs every | 2 hours automatically |
| Max per run | 5 new listings |
| Admin gets | Full details: title, price, phone, link |
| Channel gets | Clean post: title, location, selling points, photo |
| Duplicates | Tracked in `posted.json` — never resent |
| Filters | Skips listings with no phone, no image, price > ₦5M |

---

## File structure

```
telegram-bot/
├── main.py           ← Start here
├── config.py         ← Reads from .env automatically
├── scraper.py        ← Fetches listings from the web
├── filter.py         ← Quality + dedup filtering
├── caption.py        ← Dynamic channel captions
├── telegram_bot.py   ← All Telegram API calls
├── storage.py        ← posted.json read/write
├── .env              ← Your secrets (never share this)
├── .env.example      ← Template to copy from
├── requirements.txt  ← Python dependencies
└── run.sh            ← One-click start script
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Bot token error | Check `.env` — no spaces around `=` |
| Channel post fails | Make sure `@beninpropertybot` is admin in your channel |
| No listings found | Site may be temporarily down — bot will retry next cycle |
| Process killed on Android | Use `termux-wake-lock` or `tmux` (see above) |
