
import csv
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "private" / "website_discovery"

INPUT_FILE = DATA_DIR / "discovered_websites_input.csv"
OUTPUT_FILE = DATA_DIR / "discovered_websites.csv"

SUPPORTED_NICHES = [
    "business",
    "technology",
    "marketing",
    "finance",
    "health",
    "travel",
    "education",
    "lifestyle",
    "home",
    "fashion",
    "food",
    "automotive",
    "real_estate",
    "saas",
    "other"
]


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_website(value):
    value = clean_text(value).lower()

    if not value:
        return None

    if not value.startswith(("http://", "https://")):
        value = "https://" + value

    try:
        parsed = urlparse(value)

        domain = parsed.netloc.lower()
        domain = domain.split("@")[-1]
        domain = domain.split(":")[0]

        if domain.startswith("www."):
            domain = domain[4:]

        if "." not in domain or " " in domain:
            return None

        return urlunparse((
            "https",
            domain,
            "",
            "",
            "",
            ""
        ))

    except Exception:
        return None


def normalize_niche(value):
    niche = clean_text(value).lower()
    niche = niche.replace(" ", "_")

    if niche in SUPPORTED_NICHES:
        return niche

    return "other"


def process_website(record):
    website = normalize_website(record.get("website"))

    if not website:
        return None

    return {
        "website": website,
        "niche": normalize_niche(record.get("niche")),
        "source": clean_text(record.get("source")),
        "discovery_date": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "DISCOVERED"
    }


def main():
    if not INPUT_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        with open(
            INPUT_FILE,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["website", "niche", "source"]
            )
            writer.writeheader()

        print("Input CSV created.")
        print(f"Add websites to: {INPUT_FILE}")
        return

    with open(
        INPUT_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        required = {"website", "niche", "source"}

        if not required.issubset(reader.fieldnames or []):
            print("Required CSV columns are missing.")
            return

        records = list(reader)

    unique_websites = {}

    for record in records:
        result = process_website(record)

        if result:
            unique_websites[result["website"]] = result

    results = list(unique_websites.values())

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        fields = [
            "website",
            "niche",
            "source",
            "discovery_date",
            "status"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )
        writer.writeheader()
        writer.writerows(results)

    print("Website discovery processing completed.")
    print(f"Input records: {len(records)}")
    print(f"Unique valid websites: {len(results)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
