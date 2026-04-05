"""
telegram_bot.py — All Telegram API communication.

Public API:
  send_private(listing)   → sends full details to admin only
  send_public(listing)    → sends clean post (no price/phone) to channel
  handle_commands(update) → responds to /start /listings /contact /help
  get_updates(offset)     → polls for new messages
"""
import requests
import logging
from config import BOT_TOKEN, ADMIN_CHAT_ID, CHANNEL_ID, ADMIN_USERNAME
from caption import generate_caption

logger = logging.getLogger(__name__)


def _api(endpoint: str) -> str:
    return f"https://api.telegram.org/bot{BOT_TOKEN}/{endpoint}"


# ──────────────────────────────────────────────
#  Public send functions
# ──────────────────────────────────────────────

def send_private(listing: dict) -> bool:
    """
    Send FULL listing details to the admin privately.
    Includes: title, location, price, phone, direct link.
    """
    title = listing.get("title") or "Property Listing"
    location = listing.get("location") or "Benin City"
    price = listing.get("price") or "Price on request"
    phone = listing.get("phone") or "Not available"
    url = listing.get("listing_url") or "N/A"

    text = (
        f"🏠 *{title}*\n"
        f"📍 {location}\n"
        f"💰 {price}\n"
        f"📞 {phone}\n"
        f"🔗 {url}"
    )
    return _send_message(ADMIN_CHAT_ID, text)


def send_public(listing: dict) -> bool:
    """
    Send a dynamic, attractive listing to the public channel.
    NO price. NO phone. NO contact details (only DM call-to-action).
    Uses generate_caption() for engaging copy.
    """
    caption = generate_caption(listing)
    image_url = listing.get("image_url")

    if image_url:
        ok = _send_photo(CHANNEL_ID, image_url, caption)
        if ok:
            return True
        logger.warning("sendPhoto failed — falling back to text post")

    return _send_message(CHANNEL_ID, caption)


# ──────────────────────────────────────────────
#  Low-level Telegram helpers
# ──────────────────────────────────────────────

def _send_message(chat_id: str, text: str) -> bool:
    """Send a Markdown text message to any Telegram chat."""
    try:
        r = requests.post(
            _api("sendMessage"),
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=30,
        )
        data = r.json()
        if not data.get("ok"):
            logger.error(f"sendMessage failed: {data.get('description')}")
            return False
        return True
    except requests.RequestException as e:
        logger.error(f"sendMessage error: {e}")
        return False


def _send_photo(chat_id: str, photo_url: str, caption: str) -> bool:
    """Send a photo with Markdown caption."""
    try:
        r = requests.post(
            _api("sendPhoto"),
            json={
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "Markdown",
            },
            timeout=30,
        )
        data = r.json()
        if not data.get("ok"):
            logger.error(f"sendPhoto failed: {data.get('description')}")
            return False
        return True
    except requests.RequestException as e:
        logger.error(f"sendPhoto error: {e}")
        return False


# ──────────────────────────────────────────────
#  Command handler
# ──────────────────────────────────────────────

def handle_commands(update: dict) -> None:
    """Respond to /start /listings /contact /help commands."""
    message = update.get("message") or {}
    text = message.get("text", "")
    chat_id = str(message.get("chat", {}).get("id", ""))

    if not chat_id or not text.startswith("/"):
        return

    cmd = text.split()[0].split("@")[0].lower()

    if cmd == "/start":
        _send_message(
            chat_id,
            f"👋 *Welcome to Benin City Property Bot!*\n\n"
            f"We list available properties for rent across Benin City, Edo State.\n\n"
            f"📲 See our channel for listings, then DM {ADMIN_USERNAME} "
            f"for prices, inspection bookings, and full details.",
        )

    elif cmd == "/listings":
        _send_message(
            chat_id,
            f"📋 New listings are posted to our channel regularly.\n\n"
            f"Once you find one you like, contact {ADMIN_USERNAME} "
            f"for the full price and to arrange inspection.",
        )

    elif cmd == "/contact":
        _send_message(
            chat_id,
            f"📲 *Contact the Admin*\n\n"
            f"DM {ADMIN_USERNAME} directly to:\n"
            f"• Get property prices\n"
            f"• Book an inspection visit\n"
            f"• Negotiate rent terms\n\n"
            f"Serious enquiries only, please.",
        )

    elif cmd == "/help":
        _send_message(
            chat_id,
            "ℹ️ *Available Commands*\n\n"
            "/start — Welcome message\n"
            "/listings — How to find properties\n"
            "/contact — Reach the admin\n"
            "/help — This help menu",
        )


# ──────────────────────────────────────────────
#  Polling
# ──────────────────────────────────────────────

def get_updates(offset: int = None) -> list[dict]:
    """Long-poll Telegram for incoming messages."""
    params: dict = {"timeout": 10}
    if offset is not None:
        params["offset"] = offset
    try:
        r = requests.get(_api("getUpdates"), params=params, timeout=20)
        data = r.json()
        if data.get("ok"):
            return data.get("result", [])
    except requests.RequestException as e:
        logger.error(f"getUpdates error: {e}")
    return []
