#!/usr/bin/env python3
"""
Baseline-only page watcher
• Logs to the terminal on EVERY check
• Posts to Discord whenever the page differs from the first hash
"""

import hashlib, logging, time, datetime, requests, sys

# ── USER SETTINGS ────────────────────────────────────────────────────────────
URL             = "https://news.ycombinator.com/newest"
CHECK_INTERVAL  = 1                    # seconds between checks
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1386691711354273897/4fNsgr7fjKauSfmkBk411K16Qjkd3i9o7n-CJ23SFUyZAtD8-yHA8keS169QgIV9tc2B"

# ── LOGGING SETUP ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,                        # show every check
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# ── SMALL HELPERS ────────────────────────────────────────────────────────────
def hash_page(url: str) -> str:
    """Return SHA-256 of raw HTML (string)."""
    html = requests.get(url, timeout=10).text
    return hashlib.sha256(html.encode()).hexdigest()

def notify_discord(message: str) -> None:
    """Send a plain-text message to Discord; raise if it fails."""
    r = requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    if r.status_code >= 400:
        raise RuntimeError(f"Discord HTTP {r.status_code}: {r.text[:200]}")

# ── MAIN LOOP ────────────────────────────────────────────────────────────────
def main() -> None:

    print("BASELINE:", hash_page("https://studentvillage.ch/en/apply/"))

    if not DISCORD_WEBHOOK.startswith("https://"):
        sys.exit("→ Set DISCORD_WEBHOOK to a full https://discord.com/api/webhooks/... URL")

    baseline = hash_page(URL)  # one-time reference
    logging.info("Baseline hash captured.")
    try:
        # quick connectivity sanity-check
        notify_discord("🟢 Watcher started (baseline set).")
        logging.info("Start-up message sent to Discord.")
    except Exception as e:
        logging.error(f"Unable to reach Discord webhook: {e}")

    try:
        while True:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            try:
                current = hash_page(URL)
                changed = current != baseline
                logging.info(f"[{ts}] checked (changed = {changed})")
                if changed:
                    try:
                        notify_discord(f"🔄 Page changed from baseline at {ts}: {URL}")
                        logging.info("Discord notification sent.")
                    except Exception as e:
                        logging.error(f"Discord error: {e}")
            except Exception as e:
                logging.error(f"Fetch/compare error: {e}")

            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Stopped by user. Goodbye!")

if __name__ == "__main__":
    main()
