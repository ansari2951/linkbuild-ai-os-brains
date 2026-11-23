
import csv
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = ROOT / "data" / "private" / "email_extraction" / "classified_emails.csv"
OUTPUT_FILE = ROOT / "data" / "private" / "email_extraction" / "contact_intelligence.csv"


def get_website_name(url):
    try:
        host = urlparse(url).hostname or ""
        host = host.lower().removeprefix("www.")
        return host
    except Exception:
        return ""


def get_contact_type(email, category):
    email = email.lower().strip()
    local = email.split("@")[0]

    if category == "Editorial":
        return "Editor"
    if category == "Press":
        return "Press / PR"
    if category == "Marketing":
        return "Marketing"
    if category == "Advertising":
        return "Advertising"
    if category == "Partnerships":
        return "Partnerships"
    if category == "Business":
        return "Business"
    if category == "General Contact":
        return "General Contact"

    if "editor" in local:
        return "Editor"
    if "contact" in local or "info" in local:
        return "General Contact"

    return "Other"


def get_priority(contact_type, status):
    if status != "MX_FOUND":
        return "Review"

    priorities = {
        "Editor": "High",
        "Partnerships": "High",
        "Marketing": "Medium",
        "Press / PR": "Medium",
        "Advertising": "Medium",
        "Business": "Medium",
        "General Contact": "Low",
        "Other": "Review",
    }

    return priorities.get(contact_type, "Review")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    results = []

    for row in rows:
        email = row.get("email", "").strip()
        website = row.get("website", "").strip()
        category = row.get("category", "Other").strip()
        status = row.get("status", "UNKNOWN").strip()

        contact_type = get_contact_type(email, category)

        result = dict(row)
        result["website_name"] = get_website_name(website)
        result["contact_type"] = contact_type
        result["outreach_priority"] = get_priority(
            contact_type, status
        )
        result["outreach_ready"] = (
            "Review" if status == "MX_FOUND"
            and contact_type == "Other"
            else "Yes" if status == "MX_FOUND"
            else "No"
        )

        results.append(result)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fields = list(results[0].keys()) if results else [
        "email", "website_name", "contact_type",
        "outreach_priority", "outreach_ready"
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print("\nCONTACT INTELLIGENCE COMPLETED")
    print(f"Total contacts: {len(results)}")

    print("\nPriority Summary:")

    summary = {}
    for item in results:
        priority = item["outreach_priority"]
        summary[priority] = summary.get(priority, 0) + 1

    for priority, count in summary.items():
        print(f"{priority}: {count}")

    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
