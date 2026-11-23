
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = ROOT / "data" / "private" / "email_extraction" / "verified_emails.csv"
OUTPUT_FILE = ROOT / "data" / "private" / "email_extraction" / "classified_emails.csv"


def classify_email(email):
    email = email.lower().strip()
    local = email.split("@")[0]

    rules = {
        "Editorial": [
            "editor", "editorial", "content", "writer"
        ],
        "Press": [
            "press", "media", "newsroom", "pr"
        ],
        "Advertising": [
            "advertising", "ads", "ad",
            "sponsorship", "sponsor"
        ],
        "Marketing": [
            "marketing", "growth", "seo"
        ],
        "Partnerships": [
            "partner", "partnership", "collaboration"
        ],
        "General Contact": [
            "contact", "info", "hello", "support"
        ],
        "Business": [
            "business", "sales", "commercial"
        ],
    }

    for category, keywords in rules.items():
        for keyword in keywords:
            if re.search(rf"(^|[._+-]){re.escape(keyword)}($|[._+-])", local):
                return category

    return "Other"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in rows:
        row["category"] = classify_email(row.get("email", ""))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()) if rows else ["email", "category"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\nEMAIL CLASSIFICATION COMPLETED")
    print(f"Total emails: {len(rows)}")
    print("\nCategory Summary:")

    categories = {}
    for row in rows:
        category = row["category"]
        categories[category] = categories.get(category, 0) + 1

    for category, count in categories.items():
        print(f"{category}: {count}")

    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
