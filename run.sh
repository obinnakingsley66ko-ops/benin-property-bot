#!/bin/bash
# ─────────────────────────────────────────────
#  Benin City Real Estate Bot — run.sh
#  Run this script to start the bot
# ─────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "ERROR: .env file not found!"
    echo "Create one by copying .env.example:"
    echo ""
    echo "  cp .env.example .env"
    echo "  nano .env   (then fill in your BOT_TOKEN, ADMIN_CHAT_ID, CHANNEL_ID)"
    echo ""
    exit 1
fi

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Install it with:"
    echo "  pkg install python   (Termux)"
    exit 1
fi

# Install dependencies if needed
if ! python3 -c "import requests, bs4, dotenv" &> /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Starting Benin City Real Estate Bot..."
echo "Press Ctrl+C to stop"
echo ""

python3 main.py
