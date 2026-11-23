import csv
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "seo" / "competitors"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "competitors_input.csv"
OUTPUT_FILE = DATA_DIR / "competitor_analysis.csv"


def normalize_domain(value):
    value = (value or "").strip()

    if not value:
        return ""

    if not value.startswith(("http://", "https://")):
        value = "https://" + value

    parsed = urlparse(value)
    return (parsed.hostname or "").lower().removeprefix("www.")


def analyze_competitor(record):
    domain = normalize_domain(record.get("website"))

    try:
        dr = float(record.get("dr") or 0)
    except ValueError:
        dr = 0

    try:
        traffic = int(float(record.get("organic_traffic") or 0))
    except ValueError:
        traffic = 0

    try:
        backlinks = int(float(record.get("backlinks") or 0))
    except ValueError:
        backlinks = 0

    observations = []

    if not domain:
        observations.append("Missing or invalid website")

    if dr <= 0:
        observations.append("DR data missing")

    if traffic <= 0:
        observations.append("Traffic data missing")

    if backlinks <= 0:
        observations.append("Backlink data missing")

    if dr >= 50 and traffic >= 10000:
        opportunity = "STRONG_COMPETITOR"
    elif dr >= 30 or traffic >= 3000:
        opportunity = "MODERATE_COMPETITOR"
    else:
        opportunity = "LOW_DATA_OR_AUTHORITY"

    return {
        **record,
        "normalized_domain": domain,
        "competitor_category": opportunity,
        "data_quality": (
            "NEEDS_REVIEW" if observations else "DATA_AVAILABLE"
        ),
        "observations": "; ".join(observations)
    }


def run_analysis():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No competitor records found.")
        return

    results = [analyze_competitor(row) for row in records]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Analyzed {len(results)} competitor records.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_analysis()