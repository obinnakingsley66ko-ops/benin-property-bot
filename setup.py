"""
Setup helper — run this once to verify your bot token and chat IDs are working.
Usage: python setup.py
"""
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from config import BOT_TOKEN, ADMIN_CHAT_ID, CHANNEL_ID


def check_bot_token():
    print("Checking bot token...")
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
    data = r.json()
    if data.get("ok"):
        bot = data["result"]
        print(f"  ✓ Bot connected: @{bot.get('username')} ({bot.get('first_name')})")
        return True
    else:
        print(f"  ✗ Bot token invalid: {data}")
        return False


def send_test_message(chat_id: str, label: str):
    print(f"Sending test message to {label} ({chat_id})...")
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": f"✅ Setup test: bot connected successfully to {label}!",
        },
        timeout=10,
    )
    data = r.json()
    if data.get("ok"):
        print(f"  ✓ Message delivered to {label}")
    else:
        print(f"  ✗ Failed to deliver to {label}: {data}")


if __name__ == "__main__":
    print("=== Benin City Real Estate Bot — Setup Check ===\n")

    if "YOUR_BOT_TOKEN_HERE" in BOT_TOKEN:
        print("ERROR: You haven't set your BOT_TOKEN in config.py yet!")
        print("Edit telegram-bot/config.py and fill in:")
        print("  BOT_TOKEN, ADMIN_CHAT_ID, CHANNEL_ID")
        sys.exit(1)

    if check_bot_token():
        send_test_message(ADMIN_CHAT_ID, "Admin")
        send_test_message(CHANNEL_ID, "Channel")

    print("\nSetup complete! Run `python main.py` to start the bot.")
