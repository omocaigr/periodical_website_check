#!/usr/bin/env python3
import hashlib, logging, requests, datetime, os, sys

# ── USER SETTINGS ────────────────────────────────────────────────────────────
URL = "https://news.ycombinator.com/newest"
HASH_FILE = "yc_baseline_hash.txt"
WEBHOOK = "https://discord.com/api/webhooks/1386691711354273897/4fNsgr7fjKauSfmkBk411K16Qjkd3i9o7n-CJ23SFUyZAtD8-yHA8keS169QgIV9tc2B"

# ── LOGGING SETUP ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# ── HELPERS ──────────────────────────────────────────────────────────────────
def hash_page(url: str) -> str:
    html = requests.get(url, timeout=10).text
    return hashlib.sha256(html.encode()).hexdigest()

def load_baseline() -> str:
    if not os.path.exists(HASH_FILE):
        logging.error(f"{HASH_FILE} not found — commit a baseline hash first.")
        sys.exit(1)
    return open(HASH_FILE).read().strip()

def notify_discord(msg: str):
    if not WEBHOOK:
        logging.warning("DISCORD_WEBHOOK not set.")
        return
    r = requests.post(WEBHOOK, json={"content": msg}, timeout=10)
    r.raise_for_status()

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("BASELINE:", hash_page(URL))

    logging.info("Fetching current page and comparing to baseline...")
    current_hash = hash_page(URL)
    baseline = load_baseline()

    if current_hash != baseline:
        logging.info("Page content has changed!")
        notify_discord(f"🔄 Page changed from baseline at {datetime.datetime.now().isoformat()}\n{URL}")
    else:
        logging.info("No change detected.")

if __name__ == "__main__":
    main()
