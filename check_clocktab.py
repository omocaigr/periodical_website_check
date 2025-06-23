#!/usr/bin/env python3
import hashlib, logging, requests, datetime, os, sys
from bs4 import BeautifulSoup

#  ("https://news.ycombinator.com/newest", "yc_baseline_hash.txt", "full"),
# ── USER SETTINGS ────────────────────────────────────────────────────────────
TARGETS = [
    ("https://studentvillage.ch/en/apply/", "sv_baseline_hash.txt", "paragraph"),
    ("https://www.livingscience.ch/kontakt-studentenzimmer-zuerich/?L=0", "ls_baseline_hash.txt", "full"),
]
WEBHOOK = sys.argv[1]

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

def hash_paragraph(url: str) -> str:
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraph = soup.select_one('p.font_fam_normal.font_size_25.font_size_xxs_16.font_size_xs_16.color_dblue')
    if paragraph is None:
        logging.error("Paragraph not found on Student Village page.")
        sys.exit(1)
    text = paragraph.get_text(strip=True)
    normalized = ' '.join(text.split())
    return hashlib.sha256(normalized.encode()).hexdigest()

def load_baseline(file: str) -> str:
    if not os.path.exists(file):
        logging.error(f"{file} not found — commit a baseline hash first.")
        sys.exit(1)
    return open(file).read().strip()

def notify_discord(msg: str):
    if not WEBHOOK:
        logging.warning("DISCORD_WEBHOOK not set.")
        return
    r = requests.post(WEBHOOK, json={"content": msg}, timeout=10)
    r.raise_for_status()

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    for url, hash_file, mode in TARGETS:
        logging.info(f"Checking {url}")
        if mode == "paragraph":
            current_hash = hash_paragraph(url)
        else:
            current_hash = hash_page(url)

        baseline = load_baseline(hash_file)

        if current_hash != baseline:
            logging.info(f"Page content has changed: {url}")
            notify_discord(f"🔄 Page changed from baseline at {datetime.datetime.now().isoformat()}\n{url}")
        else:
            logging.info("No change detected.")

if __name__ == "__main__":
    main()
