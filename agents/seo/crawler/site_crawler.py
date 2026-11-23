
import csv
import ipaddress
import socket
import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = PROJECT_ROOT / "data" / "private" / "seo" / "crawler"
OUTPUT_FILE = OUTPUT_DIR / "crawl_results.csv"

USER_AGENT = "LinkBuildAIOSBot/1.0"
REQUEST_TIMEOUT = 12
MAX_PAGES = 100
CRAWL_DELAY = 1


def is_public_host(hostname):
    """Block localhost, private IPs and non-public destinations."""
    if not hostname:
        return False

    if hostname.lower() == "localhost":
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


def normalize_url(url):
    url = urldefrag(url.strip())[0]
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None

    if not parsed.hostname or not is_public_host(parsed.hostname):
        return None

    return url.rstrip("/")


def load_robots_parser(base_url):
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        response = requests.get(
            robots_url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            parser.parse(response.text.splitlines())
        elif response.status_code in (401, 403):
            parser.parse(["User-agent: *", "Disallow: /"])
        else:
            parser.parse([])

    except requests.RequestException:
        parser.parse(["User-agent: *", "Disallow: /"])

    return parser


def crawl_website(start_url, max_pages=MAX_PAGES):
    start_url = normalize_url(start_url)

    if not start_url:
        raise ValueError("Invalid or non-public website URL.")

    start_domain = urlparse(start_url).hostname.lower()
    robots = load_robots_parser(start_url)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    queue = deque([(start_url, 0)])
    visited = set()
    results = []

    while queue and len(visited) < max_pages:
        current_url, depth = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        if not robots.can_fetch(USER_AGENT, current_url):
            continue

        time.sleep(CRAWL_DELAY)

        record = {
            "url": current_url,
            "status_code": "",
            "depth": depth,
            "title": "",
            "meta_description": "",
            "h1_count": 0,
            "internal_links": 0,
            "external_links": 0,
            "error": ""
        }

        try:
            # Recheck destination before every request.
            if not is_public_host(urlparse(current_url).hostname):
                record["error"] = "Blocked non-public host"
                results.append(record)
                continue

            response = session.get(
                current_url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False
            )

            record["status_code"] = response.status_code

            if 300 <= response.status_code < 400:
                record["error"] = "Redirect detected"
                results.append(record)
                continue

            if response.status_code >= 400:
                record["error"] = "HTTP error"
                results.append(record)
                continue

            content_type = response.headers.get("Content-Type", "")

            if "text/html" not in content_type.lower():
                record["error"] = "Non-HTML page"
                results.append(record)
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            if soup.title:
                record["title"] = soup.title.get_text(
                    " ", strip=True
                )

            meta = soup.find(
                "meta",
                attrs={"name": lambda value: value and
                       value.lower() == "description"}
            )

            if meta:
                record["meta_description"] = meta.get("content", "")

            record["h1_count"] = len(soup.find_all("h1"))

            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(current_url, link["href"])
                target_url = normalize_url(absolute_url)

                if not target_url:
                    continue

                target_domain = urlparse(target_url).hostname.lower()

                if target_domain == start_domain:
                    record["internal_links"] += 1

                    if (
                        depth < 5
                        and target_url not in visited
                        and len(visited) + len(queue) < max_pages
                    ):
                        queue.append((target_url, depth + 1))
                else:
                    record["external_links"] += 1

        except requests.RequestException as error:
            record["error"] = str(error)

        except Exception as error:
            record["error"] = str(error)

        results.append(record)

    return results


def save_results(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not results:
        print("No crawl results to save.")
        return

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

    print(f"Saved {len(results)} page records.")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    website = input("Enter website URL: ").strip()

    try:
        pages = crawl_website(website)
        save_results(pages)
        print("Website crawling completed.")

    except ValueError as error:
        print(f"Error: {error}")
