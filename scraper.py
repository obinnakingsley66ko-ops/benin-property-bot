"""
scraper.py — Fetches property listings from Nigeria Property Centre.

Primary  : https://nigeriapropertycentre.com/for-rent?q=benin&state=edo
Fallback : https://nigeriapropertycentre.com/for-rent/edo/benin-city

Scrapes up to 3 pages per source, deduplicates by URL,
extracts: title, price, location, image_url, listing_url, phone.
"""
import time
import requests
from bs4 import BeautifulSoup
import re
import logging
from config import SCRAPE_URL, SCRAPE_URL_FALLBACK, HEADERS

logger = logging.getLogger(__name__)

BASE_URL = "https://nigeriapropertycentre.com"
MAX_PAGES = 3
PAGE_DELAY = 1.5   # seconds between page requests


def scrape_listings() -> list[dict]:
    """
    Scrape all available Benin City property listings.

    Tries the primary URL first (search form — broader results).
    Falls back to the category URL if the primary returns < 5 cards.
    Scrapes up to MAX_PAGES pages per source.
    Returns a list of unique listing dicts.
    """
    seen_urls: set[str] = set()
    listings: list[dict] = []

    # ── Primary source (search URL) ───────────────────────
    primary_results = _scrape_source(
        base_url=SCRAPE_URL,
        page_param="page",
        seen_urls=seen_urls,
    )
    listings.extend(primary_results)

    # ── Fallback (category URL) if primary is thin ────────
    if len(listings) < 5:
        logger.warning(
            f"Primary source returned only {len(listings)} listings "
            f"— trying fallback URL"
        )
        fallback_results = _scrape_source(
            base_url=SCRAPE_URL_FALLBACK,
            page_param="page",
            seen_urls=seen_urls,
        )
        listings.extend(fallback_results)

    logger.info(f"Total: {len(listings)} unique listings scraped")
    return listings


def _scrape_source(
    base_url: str,
    page_param: str,
    seen_urls: set[str],
) -> list[dict]:
    """Fetch up to MAX_PAGES pages from a single source URL."""
    results: list[dict] = []

    for page in range(1, MAX_PAGES + 1):
        if page == 1:
            url = base_url
        elif "?" in base_url:
            url = f"{base_url}&{page_param}={page}"
        else:
            url = f"{base_url}?{page_param}={page}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            break

        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.select("div.property-list")

        if not cards:
            logger.info(f"Page {page}: no listing cards found — stopping")
            break

        logger.info(f"Page {page}: {len(cards)} card(s) from {url}")

        page_count = 0
        for card in cards:
            try:
                listing = _parse_card(card)
                if not listing:
                    continue
                link = listing.get("listing_url", "")
                if link in seen_urls:
                    continue
                seen_urls.add(link)
                results.append(listing)
                page_count += 1
            except Exception as e:
                logger.warning(f"Error parsing card: {e}")

        logger.debug(f"Page {page}: {page_count} new unique listings")

        if page_count == 0:
            break   # no new results — no point going further

        if page < MAX_PAGES:
            time.sleep(PAGE_DELAY)

    return results


def _parse_card(card) -> dict | None:
    """Parse one listing card from the HTML."""

    # ── Title ────────────────────────────────────────────
    title_el = (
        card.select_one("h4.content-title") or
        card.select_one("h3[itemprop='name']") or
        card.select_one("div.wp-block-title h3")
    )
    title = title_el.get_text(strip=True) if title_el else None

    # ── Price ─────────────────────────────────────────────
    price_parts = card.select("span.price")
    price = "Price on request"
    if price_parts:
        amount_el = next(
            (el for el in price_parts
             if el.get("content") and el.get("content") != "NGN"),
            None,
        )
        if amount_el:
            amount = amount_el.get_text(strip=True)
            period_el = card.select_one("span.period")
            period = period_el.get_text(strip=True) if period_el else ""
            price = f"₦{amount} {period}".strip()

    # ── Location ──────────────────────────────────────────
    addr_el = card.select_one("address")
    if addr_el:
        location = re.sub(r"\s+", " ", addr_el.get_text(strip=True)).strip()
    else:
        location = "Benin City, Edo"

    # ── Image ─────────────────────────────────────────────
    img_el = (
        card.select_one("img[itemprop='image']") or
        card.select_one("img[data-src]") or
        card.select_one("img")
    )
    image_url = None
    if img_el:
        src = (
            img_el.get("data-src") or
            img_el.get("src") or
            img_el.get("data-lazy-src")
        )
        if src:
            if src.startswith("http"):
                image_url = src
            elif src.startswith("//"):
                image_url = "https:" + src
            elif src.startswith("/"):
                image_url = BASE_URL + src

    # ── Listing URL ───────────────────────────────────────
    link_el = card.select_one("a[href]")
    listing_url = None
    if link_el:
        href = link_el.get("href", "")
        if href.startswith("http"):
            listing_url = href
        elif href.startswith("/"):
            listing_url = BASE_URL + href

    # ── Phone ─────────────────────────────────────────────
    phone = _extract_phone(card)

    return {
        "id": listing_url or "",
        "title": title,
        "price": price,
        "location": location,
        "image_url": image_url,
        "listing_url": listing_url,
        "phone": phone,
    }


def _extract_phone(card) -> str | None:
    """Extract the first valid Nigerian mobile number from the card."""
    pattern = re.compile(r"(?:0|\+?234)[789]\d{8,9}")

    # Try the marketed-by block first (most reliable)
    marketed = card.select_one("span.marketed-by")
    if marketed:
        for el in marketed.select("strong"):
            m = pattern.search(el.get_text())
            if m:
                return m.group(0)

    # Full-card fallback
    m = pattern.search(card.get_text())
    return m.group(0) if m else None
