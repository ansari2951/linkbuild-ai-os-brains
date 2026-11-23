
from __future__ import annotations

import argparse
import csv
import json
import re
import time

from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = ROOT / "data" / "private" / "email_extraction"

USER_AGENT = (
    "LINKBUILD-AI-OS-EmailExtractor/1.0 "
    "(public business contact research)"
)

EMAIL_PATTERN = re.compile(
    r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"
)

CONTACT_KEYWORDS = (
    "contact",
    "about",
    "advertise",
    "write-for-us",
    "write-for-us",
    "editorial",
    "team",
    "staff",
    "guest-post",
    "contribute",
)

SKIP_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf", ".zip", ".mp4", ".mp3", ".css", ".js"
)


class EmailExtractor:

    def __init__(
        self,
        timeout=15,
        max_pages=10,
        delay=1.0
    ):
        self.timeout = timeout
        self.max_pages = max_pages
        self.delay = delay

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": USER_AGENT
        })

    @staticmethod
    def normalize_url(url):

        url = url.strip()

        if not url:
            return None

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return urldefrag(url)[0]

    @staticmethod
    def get_domain(url):

        return urlparse(url).netloc.lower().removeprefix("www.")

    @staticmethod
    def is_valid_email(email):

        email = email.lower().strip()

        invalid_domains = (
            "example.com",
            "example.org",
            "test.com",
            "domain.com",
        )

        if any(email.endswith("@" + domain)
               for domain in invalid_domains):
            return False

        if ".." in email:
            return False

        return True

    def fetch_page(self, url):

        try:

            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            if "text/html" not in content_type:
                return None, None

            return response.url, response.text

        except requests.RequestException as error:

            print(f"FETCH ERROR: {url} | {error}")

            return None, None

    def extract_page_data(self, html, page_url):

        soup = BeautifulSoup(html, "html.parser")

        found_emails = set()

        # Extract emails from visible page text
        text = soup.get_text(" ", strip=True)

        found_emails.update(
            EMAIL_PATTERN.findall(text)
        )

        # Extract emails from mailto links
        for anchor in soup.find_all("a", href=True):

            href = anchor["href"].strip()

            if href.lower().startswith("mailto:"):

                address = href[7:].split("?")[0]

                found_emails.update(
                    EMAIL_PATTERN.findall(address)
                )

        # Extract emails from HTML source
        found_emails.update(
            EMAIL_PATTERN.findall(html)
        )

        cleaned_emails = {
            email.lower()
            for email in found_emails
            if self.is_valid_email(email)
        }

        # Discover relevant internal links
        discovered_links = set()

        domain = self.get_domain(page_url)

        for anchor in soup.find_all("a", href=True):

            link = urljoin(page_url, anchor["href"])

            link = urldefrag(link)[0]

            parsed = urlparse(link)

            if parsed.scheme not in ("http", "https"):
                continue

            if self.get_domain(link) != domain:
                continue

            if parsed.path.lower().endswith(SKIP_EXTENSIONS):
                continue

            discovered_links.add(link)

        return cleaned_emails, discovered_links

    def scan_website(self, website):

        start_url = self.normalize_url(website)

        if not start_url:
            return []

        print(f"\nSCANNING: {start_url}")

        queue = deque([start_url])

        visited = set()

        results = {}

        domain = self.get_domain(start_url)

        while queue and len(visited) < self.max_pages:

            current_url = queue.popleft()

            if current_url in visited:
                continue

            if self.get_domain(current_url) != domain:
                continue

            visited.add(current_url)

            print(
                f"[{len(visited)}/{self.max_pages}] "
                f"Checking: {current_url}"
            )

            final_url, html = self.fetch_page(current_url)

            if not html:
                continue

            emails, links = self.extract_page_data(
                html,
                final_url
            )

            for email in emails:

                if email not in results:

                    results[email] = {
                        "email": email,
                        "website": start_url,
                        "source_url": final_url,
                    }

            # Prioritize contact-related pages
            priority_links = []

            for link in links:

                path = urlparse(link).path.lower()

                if any(
                    keyword in path
                    for keyword in CONTACT_KEYWORDS
                ):
                    priority_links.append(link)

            for link in sorted(priority_links):

                if link not in visited and link not in queue:
                    queue.appendleft(link)

            time.sleep(self.delay)

        print(
            f"COMPLETED: {start_url} | "
            f"Pages: {len(visited)} | "
            f"Emails: {len(results)}"
        )

        return list(results.values())

    def close(self):

        self.session.close()


def load_websites(input_file):

    path = Path(input_file)

    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found: {path}"
        )

    websites = []

    for line in path.read_text(
        encoding="utf-8-sig"
    ).splitlines():

        line = line.strip()

        if line and not line.startswith("#"):
            websites.append(line)

    return websites


def save_results(results):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    json_file = OUTPUT_DIR / "email_results.json"

    csv_file = OUTPUT_DIR / "email_results.csv"

    # JSON export
    with json_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    # CSV export
    fields = [
        "email",
        "website",
        "source_url"
    ]

    with csv_file.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerows(results)

    print("\nEXPORT COMPLETED")

    print(f"JSON: {json_file}")

    print(f"CSV: {csv_file}")


def main():

    parser = argparse.ArgumentParser(
        description="LINKBUILD AI OS Email Extractor"
    )

    parser.add_argument(
        "--input",
        default="knowledge/publisher/seed_urls.txt"
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=10
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0
    )

    args = parser.parse_args()

    if args.max_pages < 1 or args.delay < 0:
        parser.error(
            "max-pages must be positive and delay cannot be negative"
        )

    websites = load_websites(args.input)

    print("=" * 55)
    print("LINKBUILD AI OS - EMAIL EXTRACTOR")
    print("=" * 55)

    print(f"Websites: {len(websites)}")

    extractor = EmailExtractor(
        max_pages=args.max_pages,
        delay=args.delay
    )

    all_results = []

    try:

        for website in websites:

            results = extractor.scan_website(website)

            all_results.extend(results)

    finally:

        extractor.close()

    # Global deduplication
    unique_results = {}

    for item in all_results:

        key = (
            item["email"],
            item["website"]
        )

        unique_results[key] = item

    final_results = list(unique_results.values())

    save_results(final_results)

    print("\nRESEARCH COMPLETED")

    print(f"Total emails: {len(final_results)}")


if __name__ == "__main__":

    main()
