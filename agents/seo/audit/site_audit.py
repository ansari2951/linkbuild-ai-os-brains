import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime, timezone
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "seo" / "audits"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "site_audit_results.csv"

HEADERS = {
    "User-Agent": "LINKBUILD-AI-OS-SEO-Audit/1.0"
}


def normalize_url(url):
    url = (url or "").strip()

    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def audit_website(url):

    url = normalize_url(url)

    result = {
        "url": url,
        "http_status": "",
        "title": "",
        "meta_description": "",
        "h1_count": 0,
        "image_count": 0,
        "images_without_alt": 0,
        "canonical": "",
        "robots_meta": "",
        "audit_status": "FAILED",
        "issues": "",
        "checked_at": datetime.now(timezone.utc).isoformat()
    }

    if not url:
        result["issues"] = "Missing URL"
        return result

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
            allow_redirects=True
        )

        result["http_status"] = response.status_code

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title")
        result["title"] = title.get_text(strip=True) if title else ""

        description = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        result["meta_description"] = (
            description.get("content", "")
            if description else ""
        )

        result["h1_count"] = len(soup.find_all("h1"))

        images = soup.find_all("img")
        result["image_count"] = len(images)

        result["images_without_alt"] = sum(
            1 for image in images
            if not image.get("alt", "").strip()
        )

        canonical = soup.find(
            "link",
            rel=lambda value: value and "canonical" in value
        )

        result["canonical"] = (
            canonical.get("href", "")
            if canonical else ""
        )

        robots = soup.find(
            "meta",
            attrs={"name": "robots"}
        )

        result["robots_meta"] = (
            robots.get("content", "")
            if robots else ""
        )

        issues = []

        if not result["title"]:
            issues.append("Missing title")

        if not result["meta_description"]:
            issues.append("Missing meta description")

        if result["h1_count"] == 0:
            issues.append("Missing H1")

        if result["h1_count"] > 1:
            issues.append("Multiple H1 tags")

        if result["images_without_alt"] > 0:
            issues.append("Images missing ALT text")

        if not result["canonical"]:
            issues.append("Missing canonical tag")

        if "noindex" in result["robots_meta"].lower():
            issues.append("Page contains noindex")

        result["issues"] = "; ".join(issues)
        result["audit_status"] = "COMPLETED"

    except requests.RequestException as error:
        result["issues"] = str(error)

    except Exception as error:
        result["issues"] = str(error)

    return result


def run_audit():

    urls = input(
        "Enter website URLs separated by commas: "
    ).split(",")

    results = [
        audit_website(url)
        for url in urls
        if url.strip()
    ]

    if not results:
        print("No valid URLs supplied.")
        return

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"Audited {len(results)} websites.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_audit()