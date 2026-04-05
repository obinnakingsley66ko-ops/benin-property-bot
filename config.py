import os
from pathlib import Path

_BASE_DIR = Path(__file__).parent

try:
    from dotenv import load_dotenv
    load_dotenv(_BASE_DIR / ".env")
except ImportError:
    pass

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "7454290789")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-1003610713226")

ADMIN_USERNAME = "@Kingsley0136"

SCRAPE_URL = "https://nigeriapropertycentre.com/for-rent/edo/benin-city"
SCRAPE_URL_FALLBACK = "https://nigeriapropertycentre.com/for-rent/edo/benin"

SCRAPE_INTERVAL_SECONDS = 7200

MAX_LISTINGS_PER_RUN = 5

POSTED_JSON_FILE = str(_BASE_DIR / "posted.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://nigeriapropertycentre.com/",
}
