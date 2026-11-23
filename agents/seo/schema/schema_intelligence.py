
import csv
import ipaddress
import json
import socket
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = PROJECT_ROOT / "data" / "private" / "seo" / "schema"
OUTPUT_FILE = OUTPUT_DIR / "schema_results.csv"

USER_AGENT = "LinkBuildAIOSBot/1.0"
TIMEOUT = 15

KNOWN_TYPES = {
    "Organization",
    "Person",
    "Article",
    "NewsArticle",
    "BlogPosting",
    "Product",
    "Service",
    "FAQPage",
    "Question",
    "Answer",
    "BreadcrumbList",
    "LocalBusiness",
    "WebSite",
    "WebPage",
    "Event",
    "Recipe",
    "Review",
    "AggregateRating",
    "HowTo"
}


def is_public_host(hostname):
    if not hostname or hostname.lower() == "localhost":
        return False

    try:
        addresses = socket.getaddrinfo(hostname, None)

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                return False

        return bool(addresses)

    except (socket.gaierror, ValueError):
        return False


def fetch_page(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    if not is_public_host(parsed.hostname):
        raise ValueError("Private or invalid host blocked.")

    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
        allow_redirects=False
    )

    if response.status_code != 200:
        raise ValueError(
            f"Website returned HTTP {response.status_code}"
        )

    if "text/html" not in response.headers.get(
        "Content-Type", ""
    ).lower():
        raise ValueError("URL did not return an HTML page.")

    return response.text


def extract_types(data):
    found = []

    if isinstance(data, dict):
        schema_type = data.get("@type")

        if isinstance(schema_type, str):
            found.append(schema_type)

        elif isinstance(schema_type, list):
            found.extend(
                item for item in schema_type
                if isinstance(item, str)
            )

        for key, value in data.items():
            if key == "@type":
                continue
            found.extend(extract_types(value))

    elif isinstance(data, list):
        for item in data:
            found.extend(extract_types(item))

    return found


def analyze_schema(url):
    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all(
        "script",
        attrs={"type": "application/ld+json"}
    )

    detected_types = []
    valid_blocks = 0
    invalid_blocks = 0
    errors = []

    for index, script in enumerate(scripts, start=1):
        raw_data = script.string or script.get_text()

        try:
            data = json.loads(raw_data)

            valid_blocks += 1
            detected_types.extend(extract_types(data))

        except json.JSONDecodeError as error:
            invalid_blocks += 1
            errors.append(
                f"Block {index}: {error.msg}"
            )

    unique_types = sorted(set(detected_types))

    known_types = [
        item for item in unique_types
        if item in KNOWN_TYPES
    ]

    unknown_types = [
        item for item in unique_types
        if item not in KNOWN_TYPES
    ]

    result = {
        "url": url,
        "json_ld_blocks": len(scripts),
        "valid_blocks": valid_blocks,
        "invalid_blocks": invalid_blocks,
        "schema_types": ", ".join(unique_types),
        "known_schema_types": ", ".join(known_types),
        "other_schema_types": ", ".join(unknown_types),
        "errors": " | ".join(errors)
    }

    return result


def save_results(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"Schema analysis saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    website = input("Enter website URL: ").strip()

    try:
        result = analyze_schema(website)
        save_results([result])

        print("\nDetected Schema Types:")
        print(result["schema_types"] or "No JSON-LD schema found.")

    except Exception as error:
        print(f"Analysis failed: {error}")
