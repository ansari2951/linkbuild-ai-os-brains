import csv
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "client_orders"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "orders_input.csv"
OUTPUT_FILE = DATA_DIR / "orders.csv"

FIELDS = [
    "order_id",
    "client_name",
    "publisher_domain",
    "article_title",
    "target_url",
    "anchor_text",
    "content_type",
    "deadline",
    "status",
    "published_url",
    "notes",
    "updated_at"
]

ALLOWED_STATUSES = {
    "NEW",
    "CONTENT_PENDING",
    "CONTENT_READY",
    "SENT_TO_PUBLISHER",
    "IN_PROGRESS",
    "PUBLISHED",
    "REJECTED",
    "CANCELLED",
    "NEEDS_REVIEW"
}


def prepare_order(record):
    order = {
        field: (record.get(field) or "").strip()
        for field in FIELDS
    }

    status = order["status"].upper() or "NEW"

    if status not in ALLOWED_STATUSES:
        status = "NEEDS_REVIEW"

    order["status"] = status
    order["updated_at"] = datetime.now(timezone.utc).isoformat()

    if not order["order_id"]:
        order["status"] = "NEEDS_REVIEW"

    if order["status"] == "PUBLISHED" and not order["published_url"]:
        order["status"] = "NEEDS_REVIEW"

    return order


def load_orders():
    if not OUTPUT_FILE.exists():
        return []

    with open(OUTPUT_FILE, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def save_orders(orders):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(orders)


def import_orders():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
        incoming = list(csv.DictReader(file))

    existing = load_orders()
    order_map = {
        order["order_id"]: order
        for order in existing
        if order.get("order_id")
    }

    for record in incoming:
        order = prepare_order(record)

        if order["order_id"]:
            order_map[order["order_id"]] = order

    save_orders(list(order_map.values()))

    print(f"Imported or updated {len(incoming)} orders.")
    print(f"Order records saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    import_orders()