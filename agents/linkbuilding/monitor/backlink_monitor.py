import csv
import ipaddress
import socket
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "linkbuilding"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "backlink_monitor_input.csv"
OUTPUT_FILE = DATA_DIR / "backlink_monitor_results.csv"

REQUEST_TIMEOUT = 12
USER_AGENT = "LinkBuildMonitorBot/1.0 (+https://github.com/ansari2951/linkbuild-ai-os-brains)"


def normalize_url(url):
    url = (url or "").strip()

    if not url:
        return ""

    if "://" not in url:
        url = "https://" + url

    return url


def is_public_host(hostname):
    if not hostname or hostname.lower() == "localhost":
        return False
    try:
        for address in socket.getaddrinfo(hostname, None):
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                return False
        return True
    except (socket.gaierror, ValueError):
        return False


def validate_url(url):
    try:
        parsed = urlparse(normalize_url(url))
        return parsed.scheme in ("http", "https") and bool(parsed.netloc) and " " not in parsed.netloc
    except ValueError:
        return False


def verify_live_backlink(published_url, target_url):
    """Fetch published_url safely and check if target_url domain appears in HTML."""
    parsed_pub = urlparse(published_url)
    if not is_public_host(parsed_pub.hostname):
        return "BLOCKED_HOST", "PRIVATE_OR_INVALID_HOST"

    target_host = (urlparse(target_url).hostname or "").lower().removeprefix("www.")
    try:
        resp = requests.get(
            published_url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        http_status = str(resp.status_code)
        if resp.status_code >= 400:
            return http_status, "HTTP_ERROR"
        body_lower = resp.text.lower()
        if target_host and target_host in body_lower:
            return http_status, "LIVE_LINK_VERIFIED"
        return http_status, "TARGET_LINK_NOT_FOUND"
    except requests.RequestException as err:
        return f"ERROR:{type(err).__name__}", "CHECK_FAILED"


def analyze_backlink(record, check_live=True):
    published_url = normalize_url(record.get("published_url"))
    target_url = normalize_url(record.get("target_url"))

    live_http_status = "NOT_CHECKED"
    link_status = "NOT_VERIFIED"

    if not published_url:
        status = "MISSING_PUBLISHED_URL"
    elif not validate_url(published_url):
        status = "INVALID_URL"
    elif not target_url:
        status = "MISSING_TARGET_URL"
    elif not validate_url(target_url):
        status = "INVALID_TARGET_URL"
    elif check_live:
        live_http_status, link_status = verify_live_backlink(published_url, target_url)
        status = "VERIFIED" if link_status == "LIVE_LINK_VERIFIED" else link_status
    else:
        status = "READY_FOR_LIVE_CHECK"

    return {
        **record,
        "published_url": published_url,
        "target_url": target_url,
        "monitor_status": status,
        "last_reviewed": datetime.now(timezone.utc).isoformat(),
        "live_http_status": live_http_status,
        "link_status": link_status,
    }


def run_monitor(check_live=True):
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No backlink records found.")
        return

    results = [analyze_backlink(record, check_live=check_live) for record in records]

    fields = list(results[0].keys())

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Checked {len(results)} backlinks.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_monitor()
