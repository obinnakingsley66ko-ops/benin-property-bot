"""
storage.py — Persistent URL-based duplicate tracking via posted.json
"""
import json
import logging
import os
from datetime import datetime
from config import POSTED_JSON_FILE

logger = logging.getLogger(__name__)

_cache: set | None = None


def load_posted_urls() -> set:
    """
    Load all previously posted listing URLs from posted.json.
    Caches the result in memory for the lifetime of the process.
    Returns an empty set if the file does not exist or is corrupt.
    """
    global _cache
    if _cache is not None:
        return _cache

    if not os.path.exists(POSTED_JSON_FILE):
        _cache = set()
        return _cache

    try:
        with open(POSTED_JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        _cache = set(data.get("posted_urls", []))
        logger.info(f"Loaded {len(_cache)} previously posted URLs from posted.json")
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Could not read posted.json: {e} — starting fresh")
        _cache = set()

    return _cache


def is_duplicate(url: str) -> bool:
    """
    Return True if this listing URL has already been sent.
    Checks both the in-memory cache and the file on first call.
    """
    if not url:
        return False
    posted = load_posted_urls()
    return url in posted


def save_posted(url: str) -> None:
    """
    Mark a listing URL as posted.
    Updates both the in-memory cache and posted.json atomically.
    """
    if not url:
        return

    posted = load_posted_urls()
    if url in posted:
        return

    posted.add(url)

    try:
        with open(POSTED_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "posted_urls": sorted(posted),
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "total": len(posted),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
    except OSError as e:
        logger.error(f"Could not write posted.json: {e}")


def save_posted_url(url: str) -> None:
    """Alias for save_posted() — kept for backward compatibility."""
    save_posted(url)
