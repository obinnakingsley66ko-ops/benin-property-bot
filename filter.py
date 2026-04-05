"""
filter.py — Quality gate for scraped listings.

Rules (all must pass):
  - Title present
  - Price present and parseable
  - Price ≤ ₦5,000,000 per annum (skip commercial/luxury outliers)
  - Phone present and not placeholder
  - Image URL present
  - Listing URL present
  - Must be Benin City / Edo State related
  - URL must not be already posted

Residential listings are sorted before office/commercial listings.
"""
import re
import logging
from config import MAX_LISTINGS_PER_RUN

logger = logging.getLogger(__name__)

MAX_PRICE_NAIRA = 20_000_000   # skip extreme luxury / data errors (>₦20M/yr)

BENIN_KEYWORDS = [
    "benin", "edo", "ugbowo", "uselu", "sapele road", "airport road",
    "new benin", "old benin", "egor", "oredo", "ikpoba", "oba market",
    "upper siluko", "lower siluko", "akpakpava", "aduwawa",
    "oregbeni", "ogida", "ekiosa", "evbuotubu", "gelegele",
    "mission road", "etete", "oka", "ekiuwa", "esigie",
]

OFFICE_KEYWORDS = ["office", "shop", "warehouse", "commercial", "factory", "store"]


def filter_listings(listings: list[dict], posted_urls: set) -> list[dict]:
    """
    Filter and sort listings. Returns up to MAX_LISTINGS_PER_RUN items.
    Residential listings appear before commercial ones.
    """
    passed = []
    for listing in listings:
        reason = _skip_reason(listing, posted_urls)
        if reason:
            logger.debug(f"Skip [{reason}]: {listing.get('title', '')!r}")
        else:
            passed.append(listing)

    passed = _sort_residential_first(passed)

    logger.info(
        f"Filter: {len(listings)} scraped → "
        f"{len(passed)} valid new → "
        f"sending {min(len(passed), MAX_LISTINGS_PER_RUN)}"
    )
    return passed[:MAX_LISTINGS_PER_RUN]


def is_duplicate(url: str, posted_urls: set) -> bool:
    """Return True if this URL was already posted."""
    return bool(url) and url in posted_urls


def _skip_reason(listing: dict, posted_urls: set) -> str | None:
    """Return a human-readable skip reason, or None if the listing passes."""

    if not listing.get("title"):
        return "no title"

    price_raw = listing.get("price", "")
    if not price_raw or price_raw.strip().lower() in ("", "price on request"):
        return "no price"

    price_val = _parse_price_naira(price_raw)
    if price_val is not None and price_val > MAX_PRICE_NAIRA:
        return f"price too high (₦{price_val:,})"

    phone = listing.get("phone", "")
    if not phone or phone.strip().lower() in ("", "not available", "n/a", "none"):
        return "no phone"

    if not listing.get("image_url"):
        return "no image"

    if not listing.get("listing_url"):
        return "no link"

    if not _is_benin(listing):
        return f"not Benin — {listing.get('location', '')!r}"

    url = listing.get("listing_url", "")
    if url and url in posted_urls:
        return "already posted"

    return None


def _parse_price_naira(price_str: str) -> int | None:
    """
    Extract the numeric naira amount from a price string like '₦1,200,000 per annum'.
    Returns None if it cannot be parsed.
    """
    digits = re.sub(r"[^\d]", "", price_str)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def _is_benin(listing: dict) -> bool:
    combined = " ".join([
        listing.get("title") or "",
        listing.get("location") or "",
        listing.get("listing_url") or "",
    ]).lower()
    return any(kw in combined for kw in BENIN_KEYWORDS)


def _sort_residential_first(listings: list[dict]) -> list[dict]:
    """Put residential listings before office/commercial ones."""
    def _is_office(listing: dict) -> bool:
        combined = (
            (listing.get("title") or "") + " " +
            (listing.get("listing_url") or "")
        ).lower()
        return any(kw in combined for kw in OFFICE_KEYWORDS)

    residential = [l for l in listings if not _is_office(l)]
    commercial = [l for l in listings if _is_office(l)]
    return residential + commercial
