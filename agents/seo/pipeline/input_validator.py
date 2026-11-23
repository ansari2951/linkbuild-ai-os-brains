
from pathlib import Path
from urllib.parse import urlparse
import csv
import ipaddress
import socket


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "pipeline"
    / "websites_input.csv"
)

MAX_WEBSITES_PER_RUN = 10


def is_valid_url(url):
    if not url:
        return False, "Empty URL"

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False, "URL must start with http:// or https://"

    if not parsed.hostname:
        return False, "Invalid hostname"

    if parsed.username or parsed.password:
        return False, "URLs containing credentials are not allowed"

    try:
        ipaddress.ip_address(parsed.hostname)
        return False, "IP-address URLs are not allowed"

    except ValueError:
        pass

    try:
        addresses = socket.getaddrinfo(
            parsed.hostname,
            None,
            type=socket.SOCK_STREAM
        )

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                return False, "Private or non-public host is not allowed"

    except socket.gaierror:
        return False, "Hostname could not be resolved"

    return True, "Valid URL"


def validate_input_file():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {INPUT_FILE}"
        )

    valid_urls = []
    rejected_urls = []
    seen_urls = set()

    with open(
        INPUT_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames or "website_url" not in reader.fieldnames:
            raise ValueError(
                "CSV must contain a website_url column"
            )

        for row_number, row in enumerate(reader, start=2):
            url = (row.get("website_url") or "").strip()

            if not url:
                rejected_urls.append({
                    "row": row_number,
                    "url": "",
                    "reason": "Empty URL"
                })
                continue

            normalized_url = url.rstrip("/").lower()

            if normalized_url in seen_urls:
                rejected_urls.append({
                    "row": row_number,
                    "url": url,
                    "reason": "Duplicate URL"
                })
                continue

            seen_urls.add(normalized_url)

            valid, reason = is_valid_url(url)

            if valid:
                valid_urls.append(url)
            else:
                rejected_urls.append({
                    "row": row_number,
                    "url": url,
                    "reason": reason
                })

    if len(valid_urls) > MAX_WEBSITES_PER_RUN:
        rejected_urls.extend({
            "row": "",
            "url": url,
            "reason": "Maximum websites per run exceeded"
        } for url in valid_urls[MAX_WEBSITES_PER_RUN:])

        valid_urls = valid_urls[:MAX_WEBSITES_PER_RUN]

    return valid_urls, rejected_urls


def main():
    valid_urls, rejected_urls = validate_input_file()

    print("\n===== SEO INPUT VALIDATION =====")
    print(f"Valid websites: {len(valid_urls)}")
    print(f"Rejected entries: {len(rejected_urls)}")

    for url in valid_urls:
        print(f"VALID: {url}")

    for item in rejected_urls:
        print(
            f"REJECTED: {item['url']} | {item['reason']}"
        )

    return valid_urls, rejected_urls


if __name__ == "__main__":
    main()
