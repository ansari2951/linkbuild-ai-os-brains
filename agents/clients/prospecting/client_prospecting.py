
import csv
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "private" / "client_prospecting"

INPUT_FILE = DATA_DIR / "prospects_input.csv"
OUTPUT_FILE = DATA_DIR / "client_prospects.csv"

TARGET_SERVICES = [
    "seo",
    "link building",
    "guest posting",
    "digital marketing",
    "content marketing",
    "digital pr",
    "saas marketing",
    "geo",
    "aeo"
]


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_website(value):
    value = clean_text(value).lower()

    if not value:
        return ""

    if not value.startswith(("http://", "https://")):
        value = "https://" + value

    try:
        parsed = urlparse(value)
        domain = parsed.netloc.split("@")[-1].split(":")[0]

        if domain.startswith("www."):
            domain = domain[4:]

        if "." not in domain or " " in domain:
            return ""

        return urlunparse(("https", domain, "", "", "", ""))

    except Exception:
        return ""


def calculate_priority(record):
    score = 0

    services = clean_text(record.get("services")).lower()
    company_type = clean_text(record.get("company_type")).lower()
    contact_email = clean_text(record.get("email"))

    if any(service in services for service in TARGET_SERVICES):
        score += 40

    if "agency" in company_type:
        score += 25

    if "marketing" in company_type:
        score += 15

    if contact_email and "@" in contact_email:
        score += 20

    if score >= 60:
        return score, "HIGH"

    if score >= 35:
        return score, "MEDIUM"

    return score, "LOW"


def process_prospect(record):
    website = normalize_website(record.get("website"))

    if not website:
        return None

    score, priority = calculate_priority(record)

    return {
        "company_name": clean_text(record.get("company_name")),
        "website": website,
        "company_type": clean_text(record.get("company_type")),
        "services": clean_text(record.get("services")),
        "niche": clean_text(record.get("niche")),
        "contact_name": clean_text(record.get("contact_name")),
        "email": clean_text(record.get("email")),
        "country": clean_text(record.get("country")),
        "priority_score": score,
        "priority": priority,
        "status": "NEW",
        "discovered_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        with open(
            INPUT_FILE,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "company_name",
                    "website",
                    "company_type",
                    "services",
                    "niche",
                    "contact_name",
                    "email",
                    "country"
                ]
            )
            writer.writeheader()

        print("Prospect input file created.")
        print(f"Add prospect data to: {INPUT_FILE}")
        return

    with open(
        INPUT_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        required = {"company_name", "website"}

        if not required.issubset(reader.fieldnames or []):
            print("Required CSV columns are missing.")
            return

        records = list(reader)

    unique_prospects = {}

    for record in records:
        result = process_prospect(record)

        if result:
            unique_prospects[result["website"]] = result

    results = list(unique_prospects.values())

    results.sort(
        key=lambda item: item["priority_score"],
        reverse=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys() if results else [
                "company_name", "website", "company_type",
                "services", "niche", "contact_name", "email",
                "country", "priority_score", "priority",
                "status", "discovered_at"
            ]
        )
        writer.writeheader()
        writer.writerows(results)

    print("Client prospecting processing completed.")
    print(f"Input records: {len(records)}")
    print(f"Unique prospects: {len(results)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
