
import csv
import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = PROJECT_ROOT / "data" / "private" / "seo" / "indexing"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_FILE = OUTPUT_DIR / "indexing_report.csv"
SITEMAP_FILE = OUTPUT_DIR / "sitemap_urls.csv"

USER_AGENT = "LinkBuildAIOSBot/1.0"
TIMEOUT = 15


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


def safe_get(url):
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

    return response


def get_robots_info(base_url):
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    result = {
        "robots_url": robots_url,
        "robots_status": "NOT_FOUND",
        "allow_rules": 0,
        "disallow_rules": 0,
        "sitemaps_declared": []
    }

    try:
        response = safe_get(robots_url)
        result["robots_status"] = str(response.status_code)

        if response.status_code != 200:
            return result

        for line in response.text.splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, separator, value = line.partition(":")

            if not separator:
                continue

            key = key.strip().lower()
            value = value.strip()

            if key == "allow":
                result["allow_rules"] += 1

            elif key == "disallow":
                result["disallow_rules"] += 1

            elif key == "sitemap" and value.startswith(
                ("http://", "https://")
            ):
                result["sitemaps_declared"].append(value)

    except Exception as error:
        result["robots_status"] = f"ERROR: {error}"

    return result


def discover_sitemaps(base_url, declared_sitemaps):
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"

    candidates = list(declared_sitemaps)

    candidates.extend([
        f"{root}/sitemap.xml",
        f"{root}/sitemap_index.xml",
        f"{root}/wp-sitemap.xml"
    ])

    unique = []

    for sitemap in candidates:
        if sitemap not in unique:
            unique.append(sitemap)

    return unique


def extract_sitemap_urls(sitemap_url, visited=None, limit=5000):
    if visited is None:
        visited = set()

    if sitemap_url in visited or len(visited) >= 20:
        return []

    visited.add(sitemap_url)

    try:
        response = safe_get(sitemap_url)

        if response.status_code != 200:
            return []

        if len(response.content) > 10 * 1024 * 1024:
            return []

        root = ET.fromstring(response.content)

        urls = []

        for element in root:
            tag = element.tag.split("}")[-1].lower()

            if tag == "loc" and element.text:
                urls.append(element.text.strip())

            elif tag == "sitemap":
                for child in element:
                    if child.tag.split("}")[-1].lower() == "loc":
                        if child.text:
                            child_url = child.text.strip()

                            urls.extend(
                                extract_sitemap_urls(
                                    child_url,
                                    visited,
                                    limit
                                )
                            )

            if len(urls) >= limit:
                break

        return urls[:limit]

    except Exception:
        return []


def analyze_website(base_url):
    parsed = urlparse(base_url.strip())

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Enter a valid website URL.")

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    if not is_public_host(parsed.hostname):
        raise ValueError("Private or invalid website blocked.")

    robots = get_robots_info(base_url)

    sitemap_candidates = discover_sitemaps(
        base_url,
        robots["sitemaps_declared"]
    )

    sitemap_urls = []
    found_sitemap = ""

    for sitemap in sitemap_candidates:
        urls = extract_sitemap_urls(sitemap)

        if urls:
            sitemap_urls = urls
            found_sitemap = sitemap
            break

    report = {
        "website": base_url,
        "robots_status": robots["robots_status"],
        "allow_rules": robots["allow_rules"],
        "disallow_rules": robots["disallow_rules"],
        "sitemap_found": "YES" if found_sitemap else "NO",
        "sitemap_location": found_sitemap,
        "sitemap_url_count": len(sitemap_urls)
    }

    return report, sitemap_urls


def save_report(report, sitemap_urls):
    with open(
        REPORT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(report.keys())
        )
        writer.writeheader()
        writer.writerow(report)

    with open(
        SITEMAP_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["sitemap_url"])

        for url in sitemap_urls:
            writer.writerow([url])

    print("Indexing analysis saved.")
    print(f"Report: {REPORT_FILE}")
    print(f"Sitemap URLs: {SITEMAP_FILE}")


if __name__ == "__main__":
    website = input("Enter website URL: ").strip()

    try:
        report, sitemap_urls = analyze_website(website)
        save_report(report, sitemap_urls)

    except Exception as error:
        print(f"Analysis failed: {error}")
