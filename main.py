"""
main.py — Entry point for the Benin City Real Estate Bot.

Cycle (every 2 hours):
  1. Scrape listings from Nigeria Property Centre (Benin City)
  2. Filter: quality checks + dedup + price cap + Benin keyword
  3. For each new listing (max 5 per run):
       a. Send FULL details privately to admin
       b. Send CLEAN attractive post to public channel
       c. Save URL to posted.json only if BOTH sends succeed
       d. Wait 2 seconds before next listing
  4. Sleep until next cycle

Command listener runs in a background thread.
"""
import time
import logging
import threading

from config import SCRAPE_INTERVAL_SECONDS, MAX_LISTINGS_PER_RUN
from scraper import scrape_listings
from filter import filter_listings, is_duplicate
from telegram_bot import send_private, send_public, handle_commands, get_updates
from storage import load_posted_urls, save_posted, is_duplicate as storage_is_duplicate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SEND_DELAY_SECONDS = 2


def run_scraper_cycle(posted_urls: set) -> None:
    """Run one full scrape → filter → send cycle."""
    logger.info("=" * 55)
    logger.info("CYCLE START")

    listings = scrape_listings()
    if not listings:
        logger.warning("No listings scraped — check connection or site structure")
        logger.info("=" * 55)
        return

    new_listings = filter_listings(listings, posted_urls)
    if not new_listings:
        logger.info("No new listings passed all filters")
        logger.info("=" * 55)
        return

    logger.info(f"Processing {len(new_listings)} listing(s) this cycle")

    sent_ok = 0
    seen_this_run: set[str] = set()

    for i, listing in enumerate(new_listings, start=1):
        title = listing.get("title", "untitled")
        url = listing.get("listing_url", "")

        # In-run dedup safety check (belt and braces)
        if url in seen_this_run:
            logger.warning(f"[{i}] In-run duplicate skipped: {url}")
            continue
        if storage_is_duplicate(url):
            logger.warning(f"[{i}] Already in posted.json, skipping: {title!r}")
            continue

        seen_this_run.add(url)
        logger.info(f"[{i}/{len(new_listings)}] {title!r}")

        try:
            # ── Step 1: private message to admin ──
            private_ok = send_private(listing)
            if private_ok:
                logger.info("  ✓ Private → admin")
            else:
                logger.warning("  ✗ Private FAILED")

            time.sleep(1)

            # ── Step 2: public post to channel ──
            public_ok = send_public(listing)
            if public_ok:
                logger.info("  ✓ Public → channel")
            else:
                logger.warning("  ✗ Channel FAILED — will retry next cycle")

            # ── Step 3: persist only on full success ──
            if private_ok and public_ok:
                posted_urls.add(url)
                save_posted(url)
                sent_ok += 1
                logger.info("  ✓ Saved to posted.json")
            else:
                logger.warning("  ⚠ NOT saved — will retry next cycle")

        except Exception as e:
            logger.error(f"  Error on listing {i}: {e}")

        # Delay between listings (skip after last one)
        if i < len(new_listings):
            time.sleep(SEND_DELAY_SECONDS)

    logger.info(f"CYCLE END — {sent_ok}/{len(new_listings)} posted successfully")
    logger.info("=" * 55)


def run_command_listener() -> None:
    """
    Background thread: long-polls Telegram for user commands.
    Handles /start /listings /contact /help
    """
    logger.info("Command listener running")
    offset = None
    while True:
        try:
            updates = get_updates(offset=offset)
            for update in updates:
                try:
                    handle_commands(update)
                except Exception as e:
                    logger.error(f"Command error: {e}")
                offset = update["update_id"] + 1
        except Exception as e:
            logger.error(f"Listener error: {e}")
        time.sleep(2)


def main() -> None:
    logger.info("🏠 Benin City Real Estate Bot — starting up")
    logger.info(f"  Data source : nigeriapropertycentre.com/for-rent/edo/benin-city")
    logger.info(f"  Run interval: every {SCRAPE_INTERVAL_SECONDS // 60} minutes")
    logger.info(f"  Max per run : {MAX_LISTINGS_PER_RUN} listings")
    logger.info(f"  Send delay  : {SEND_DELAY_SECONDS}s between each listing")

    posted_urls = load_posted_urls()

    threading.Thread(
        target=run_command_listener,
        daemon=True,
        name="CommandListener",
    ).start()

    while True:
        try:
            run_scraper_cycle(posted_urls)
        except Exception as e:
            logger.error(f"Unhandled cycle error: {e}")

        logger.info(f"Sleeping {SCRAPE_INTERVAL_SECONDS // 60} min until next cycle...")
        time.sleep(SCRAPE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
