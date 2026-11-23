import csv
import json
import re
import time
import argparse
import ipaddress

from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser


ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = ROOT / "knowledge" / "publisher" / "seed_urls.txt"
OUTPUT_DIR = ROOT / "data" / "private" / "publisher_research"

MAX_BYTES = 1_000_000
TIMEOUT = 25


class PageParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.text = []
        self.links = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "title":
            self.in_title = True

        if tag == "meta":
            name = attrs.get("name", "").lower()

            if name == "description":
                self.description = attrs.get("content", "")

        if tag == "a":
            href = attrs.get("href", "")

            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        clean = data.strip()

        if not clean:
            return

        if self.in_title:
            self.title += " " + clean

        if len(self.text) < 500:
            self.text.append(clean)


def validate_url(url):

    url = url.strip()

    if not url:
        raise ValueError("Empty URL")

    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS are allowed")

    if not parsed.hostname:
        raise ValueError("Invalid hostname")

    host = parsed.hostname.lower()

    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("Local addresses are not allowed")

    try:
        address = ipaddress.ip_address(host)

        if not address.is_global:
            raise ValueError("Non-public IP addresses are not allowed")

    except ValueError as error:
        if "not allowed" in str(error):
            raise

    return url


def calculate_relevance(niche, title, description, text):

    keywords = set(re.findall(r"[a-z0-9]+", niche.lower()))

    if not keywords:
        return 0

    content = (
        title + " " + description + " " + text
    ).lower()

    matches = sum(1 for word in keywords if word in content)

    return round((matches / len(keywords)) * 100)


def inspect_website(url, niche):

    record = {
        "url": url,
        "status": "unknown",
        "http_status": None,
        "title": "",
        "description": "",
        "relevance_score": 0,
        "contact_pages": [],
        "public_emails": [],
        "error": ""
    }

    try:
        url = validate_url(url)

        request = Request(
            url,
            headers={
                "User-Agent": "LinkBuildResearchBot/1.0 (website quality research)"
            }
        )

        with urlopen(request, timeout=TIMEOUT) as response:

            status = response.status
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "")

            record["http_status"] = status
            record["url"] = final_url

            if "text/html" not in content_type.lower():
                record["status"] = "non_html"
                return record

            html = response.read(MAX_BYTES).decode(
                "utf-8",
                errors="replace"
            )

        parser = PageParser()
        parser.feed(html)

        title = parser.title.strip()
        description = parser.description.strip()
        text = " ".join(parser.text)

        record["title"] = title
        record["description"] = description

        record["relevance_score"] = calculate_relevance(
            niche,
            title,
            description,
            text
        )

        for href in parser.links:

            absolute = urljoin(final_url, href)
            lower = href.lower()

            if lower.startswith("mailto:"):
                email = href[7:].split("?")[0].strip()

                if email and email not in record["public_emails"]:
                    record["public_emails"].append(email)

            elif any(word in lower for word in (
                "contact",
                "about",
                "advertise",
                "write-for-us",
                "contribute",
                "guest-post"
            )):
                if urlparse(absolute).netloc == urlparse(final_url).netloc:
                    if absolute not in record["contact_pages"]:
                        record["contact_pages"].append(absolute)

        emails = re.findall(
            r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
            html,
            flags=re.I
        )

        for email in emails:
            if email not in record["public_emails"]:
                record["public_emails"].append(email)

        record["status"] = "inspected"

    except HTTPError as error:

        if error.code == 429:
            record["status"] = "rate_limited"
            retry_after = error.headers.get("Retry-After")

            record["error"] = (
                f"HTTP 429: Too many requests. "
                f"Retry-After: {retry_after or 'Not provided'}"
            )

        else:
            record["status"] = "failed"
            record["error"] = str(error)[:300]

    except (URLError, TimeoutError, ValueError, OSError) as error:

        record["status"] = "failed"
        record["error"] = str(error)[:300]

    except Exception as error:

        record["status"] = "failed"
        record["error"] = str(error)[:300]

    return record


def save_results(records, niche):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    json_file = OUTPUT_DIR / "publisher_results.json"
    csv_file = OUTPUT_DIR / "publisher_results.csv"

    with json_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    fields = [
        "url",
        "status",
        "http_status",
        "title",
        "description",
        "relevance_score",
        "contact_pages",
        "public_emails",
        "error"
    ]

    with csv_file.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for record in records:
            row = record.copy()
            row["contact_pages"] = "; ".join(row["contact_pages"])
            row["public_emails"] = "; ".join(row["public_emails"])
            writer.writerow(row)

    return json_file, csv_file


def run_research(niche):

    if not INPUT_FILE.exists():
        print("Publisher URL input file not found.")
        return

    urls = [
        line.strip()
        for line in INPUT_FILE.read_text(
            encoding="utf-8-sig"
        ).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    urls = list(dict.fromkeys(urls))

    if not urls:
        print("No publisher URLs found.")
        print("Add website URLs to knowledge/publisher/seed_urls.txt")
        return

    print(f"Researching {len(urls)} website(s)...")

    records = []

    for index, url in enumerate(urls, start=1):

        print(f"[{index}/{len(urls)}] Inspecting {url}")

        result = inspect_website(url, niche)
        records.append(result)

        print(
            f"Status: {result['status']} | "
            f"Relevance: {result['relevance_score']}%"
        )

        time.sleep(2)

    json_file, csv_file = save_results(records, niche)

    print("\nRESEARCH COMPLETED")
    print(f"JSON: {json_file}")
    print(f"CSV: {csv_file}")


if __name__ == "__main__":

    cli = argparse.ArgumentParser()

    cli.add_argument(
        "--niche",
        required=True,
        help="Target publisher niche"
    )

    args = cli.parse_args()

    run_research(args.niche)
