
import csv
import ipaddress
import socket
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "internal_links"
)

OUTPUT_FILE = OUTPUT_DIR / "internal_link_audit.csv"

USER_AGENT = "LinkBuildAIOSBot/1.0"
TIMEOUT = 15
MAX_LINKS = 2000

GENERIC_ANCHORS = {
    "click here",
    "read more",
    "learn more",
    "here",
    "more",
    "visit",
    "know more",
    "click"
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


def validate_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed.hostname or not is_public_host(parsed.hostname):
        raise ValueError("Private or invalid host blocked.")

    return url


def normalize_domain(domain):
    return domain.lower().removeprefix("www.")


def analyze_internal_links(page_url):
    validate_url(page_url)

    response = requests.get(
        page_url,
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
        raise ValueError("URL did not return HTML.")

    soup = BeautifulSoup(response.text, "html.parser")

    source_domain = normalize_domain(
        urlparse(page_url).hostname
    )

    links = []
    target_counter = Counter()

    for anchor in soup.find_all("a", href=True)[:MAX_LINKS]:
        raw_url = anchor.get("href", "").strip()

        if not raw_url:
            continue

        absolute_url = urljoin(page_url, raw_url)
        absolute_url = urldefrag(absolute_url)[0]

        parsed = urlparse(absolute_url)

        if parsed.scheme not in ("http", "https"):
            continue

        if not parsed.hostname:
            continue

        target_domain = normalize_domain(parsed.hostname)

        link_type = (
            "INTERNAL"
            if target_domain == source_domain
            else "EXTERNAL"
        )

        anchor_text = anchor.get_text(
            " ",
            strip=True
        )

        if not anchor_text and anchor.find("img"):
            anchor_text = (
                anchor.find("img").get("alt", "").strip()
            )

        if not anchor_text:
            anchor_status = "EMPTY"
        elif anchor_text.lower() in GENERIC_ANCHORS:
            anchor_status = "GENERIC"
        else:
            anchor_status = "DESCRIPTIVE"

        target_counter[absolute_url] += 1

        links.append({
            "source_page": page_url,
            "target_url": absolute_url,
            "link_type": link_type,
            "anchor_text": anchor_text,
            "anchor_status": anchor_status,
            "nofollow": "nofollow" in (
                anchor.get("rel") or []
            ),
            "opens_new_tab": anchor.get("target") == "_blank",
            "duplicate_link": False
        })

    for item in links:
        if item["link_type"] == "INTERNAL":
            item["duplicate_link"] = (
                target_counter[item["target_url"]] > 1
            )

    return links


DEFAULT_LINK_FIELDS = [
    "source_page", "target_url", "link_type", "anchor_text",
    "anchor_status", "nofollow", "opens_new_tab", "duplicate_link"
]


def save_results(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = list(results[0].keys()) if results else DEFAULT_LINK_FIELDS

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        if results:
            writer.writerows(results)

    if not results:
        print("No links found. Empty report saved.")
    else:
        print(f"Internal link report saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    website = input("Enter website page URL: ").strip()

    try:
        results = analyze_internal_links(website)
        save_results(results)

        internal = [
            item for item in results
            if item["link_type"] == "INTERNAL"
        ]

        external = [
            item for item in results
            if item["link_type"] == "EXTERNAL"
        ]

        empty = [
            item for item in results
            if item["anchor_status"] == "EMPTY"
        ]

        generic = [
            item for item in results
            if item["anchor_status"] == "GENERIC"
        ]

        print("\nInternal Link Summary")
        print("Total links:", len(results))
        print("Internal links:", len(internal))
        print("External links:", len(external))
        print("Empty anchor text:", len(empty))
        print("Generic anchor text:", len(generic))

    except Exception as error:
        print(f"Analysis failed: {error}")
