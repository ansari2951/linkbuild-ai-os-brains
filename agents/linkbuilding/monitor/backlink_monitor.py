import csv
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "linkbuilding"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "backlink_monitor_input.csv"
OUTPUT_FILE = DATA_DIR / "backlink_monitor_results.csv"


def normalize_url(url):
    url = (url or "").strip()

    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def validate_url(url):
    try:
        parsed = urlparse(normalize_url(url))
        return bool(parsed.scheme and parsed.netloc)
    except ValueError:
        return False


def analyze_backlink(record):

    published_url = normalize_url(record.get("published_url"))
    target_url = normalize_url(record.get("target_url"))

    if not published_url:
        status = "MISSING_PUBLISHED_URL"
    elif not validate_url(published_url):
        status = "INVALID_URL"
    elif not target_url:
        status = "MISSING_TARGET_URL"
    elif not validate_url(target_url):
        status = "INVALID_TARGET_URL"
    else:
        status = "READY_FOR_LIVE_CHECK"

    return {
        **record,
        "published_url": published_url,
        "target_url": target_url,
        "monitor_status": status,
        "last_reviewed": datetime.now(timezone.utc).isoformat(),
        "live_http_status": "NOT_CHECKED",
        "link_status": "NOT_VERIFIED"
    }


def run_monitor():

    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No backlink records found.")
        return

    results = [analyze_backlink(record) for record in records]

    fields = list(results[0].keys())

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Prepared {len(results)} backlinks for monitoring.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_monitor()