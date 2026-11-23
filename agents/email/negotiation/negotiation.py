
import csv
import re
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "private" / "email_extraction"

INPUT_FILE = DATA_DIR / "negotiation_data.csv"
OUTPUT_FILE = DATA_DIR / "negotiation_results.csv"


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def get_price(value):
    if value is None:
        return None

    text = str(value).replace(",", "")
    match = re.search(r"\d+(?:\.\d{1,2})?", text)

    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def analyze_negotiation(publisher_price, offered_price, target_price):
    if publisher_price is None or offered_price is None:
        return "NEEDS_REVIEW", "Price information is incomplete."

    if publisher_price <= 0 or offered_price <= 0:
        return "NEEDS_REVIEW", "Prices must be greater than zero."

    if publisher_price <= offered_price:
        return "ACCEPT_SUGGESTION", "Publisher price is within your offer."

    if target_price is not None and target_price > 0:
        if publisher_price <= target_price:
            return "COUNTER_OFFER", "Publisher price is within your maximum budget."

    return "COUNTER_OFFER", "Publisher price is higher than your offer."


def create_reply(publisher_name, publisher_price, offered_price, currency):
    name = clean_text(publisher_name) or "there"
    currency = clean_text(currency) or "USD"

    if publisher_price is None or offered_price is None:
        return (
            f"Hello {name},\n\n"
            "Thank you for sharing your pricing details. "
            "Could you please confirm your final rate so we can "
            "review the collaboration?\n\n"
            "Best regards"
        )

    if publisher_price <= offered_price:
        return (
            f"Hello {name},\n\n"
            "Thank you for sharing your pricing. "
            "Your rate works for us. Please share the next steps "
            "and publishing requirements.\n\n"
            "Best regards"
        )

    return (
        f"Hello {name},\n\n"
        "Thank you for getting back to us. "
        f"Our current offer is {currency} {offered_price:.2f}. "
        "Would you be open to working within this budget? "
        "We would appreciate your consideration.\n\n"
        "Best regards"
    )


def process_record(record):
    publisher_price = get_price(record.get("publisher_price"))
    offered_price = get_price(record.get("offered_price"))
    target_price = get_price(record.get("target_price"))

    decision, reason = analyze_negotiation(
        publisher_price,
        offered_price,
        target_price
    )

    currency = clean_text(record.get("currency")) or "USD"

    reply = create_reply(
        record.get("publisher_name"),
        publisher_price,
        offered_price,
        currency
    )

    return {
        "publisher_name": clean_text(record.get("publisher_name")),
        "website": clean_text(record.get("website")),
        "publisher_price": publisher_price,
        "offered_price": offered_price,
        "target_price": target_price,
        "currency": currency,
        "decision_suggestion": decision,
        "reason": reason,
        "reply_draft": reply,
        "approval_status": "PENDING",
        "created_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        print(
            "Expected columns: publisher_name, website, "
            "publisher_price, offered_price, target_price, currency"
        )
        return

    with open(
        INPUT_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        required = {
            "publisher_name",
            "website",
            "publisher_price",
            "offered_price"
        }

        if not required.issubset(reader.fieldnames or []):
            print("Required CSV columns are missing.")
            return

        records = list(reader)

    if not records:
        print("No negotiation records found.")
        return

    results = [process_record(record) for record in records]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print("Negotiation analysis completed.")
    print(f"Total records: {len(results)}")
    print(f"Output: {OUTPUT_FILE}")
    print("All reply drafts require manual approval.")


if __name__ == "__main__":
    main()
