import csv
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "linkbuilding"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "placements_input.csv"
OUTPUT_FILE = DATA_DIR / "placement_tracker.csv"


FIELDS = [
    "client_name",
    "publisher_domain",
    "target_url",
    "published_url",
    "anchor_text",
    "placement_type",
    "order_id",
    "status",
    "last_checked",
    "notes"
]


def normalize_status(status):
    allowed = {
        "PENDING",
        "IN_PROGRESS",
        "PUBLISHED",
        "LIVE",
        "REMOVED",
        "REJECTED",
        "NEEDS_REVIEW"
    }

    status = (status or "PENDING").strip().upper()

    return status if status in allowed else "NEEDS_REVIEW"


def prepare_placement(record):

    result = {
        field: (record.get(field) or "").strip()
        for field in FIELDS
    }

    result["status"] = normalize_status(result["status"])

    if not result["last_checked"]:
        result["last_checked"] = datetime.now(
            timezone.utc
        ).isoformat()

    if result["status"] in {"PUBLISHED", "LIVE"}:
        if not result["published_url"]:
            result["status"] = "NEEDS_REVIEW"
            result["notes"] = (
                result["notes"] + " | Missing published URL"
            ).strip(" |")

    return result


def run_tracker():

    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No placement records found.")
        return

    results = [prepare_placement(record) for record in records]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Processed {len(results)} placement records.")
    print(f"Tracker saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_tracker()