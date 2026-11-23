import csv
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "client_reports"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ORDERS_FILE = (
    PROJECT_ROOT / "data" / "private" /
    "client_orders" / "orders.csv"
)

PLACEMENTS_FILE = (
    PROJECT_ROOT / "data" / "private" /
    "linkbuilding" / "placement_tracker.csv"
)

REPORTS_DIR = PROJECT_ROOT / "data" / "exports" / "client_reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def generate_report(client_name):

    orders = read_csv(ORDERS_FILE)
    placements = read_csv(PLACEMENTS_FILE)

    client_orders = [
        row for row in orders
        if row.get("client_name", "").strip().lower()
        == client_name.strip().lower()
    ]

    client_placements = [
        row for row in placements
        if row.get("client_name", "").strip().lower()
        == client_name.strip().lower()
    ]

    if not client_orders and not client_placements:
        print("No records found for this client.")
        return

    status_counts = Counter(
        row.get("status", "UNKNOWN")
        for row in client_orders
    )

    published = sum(
        1 for row in client_placements
        if row.get("status", "").upper()
        in {"PUBLISHED", "LIVE"}
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    safe_name = "".join(
        char if char.isalnum() else "_"
        for char in client_name
    )

    report_file = REPORTS_DIR / f"{safe_name}_{timestamp}.csv"

    rows = [
        {"metric": "Client", "value": client_name},
        {"metric": "Total Orders", "value": len(client_orders)},
        {"metric": "Total Placement Records", "value": len(client_placements)},
        {"metric": "Published Placements", "value": published},
    ]

    for status, count in status_counts.items():
        rows.append({
            "metric": f"Orders: {status}",
            "value": count
        })

    with open(report_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Client report created: {report_file}")


if __name__ == "__main__":
    client = input("Enter client name: ").strip()

    if client:
        generate_report(client)