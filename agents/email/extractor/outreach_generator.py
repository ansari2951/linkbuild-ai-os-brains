
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "private"
    / "email_extraction"
    / "contact_intelligence.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "private"
    / "email_extraction"
)

OUTPUT_FILE = OUTPUT_DIR / "outreach_drafts.csv"


def generate_email(contact):
    email = contact.get("email", "").strip()
    website = contact.get("website_name", "").strip()
    contact_type = contact.get("contact_type", "").strip()
    priority = contact.get("outreach_priority", "").strip()

    if contact_type == "Press / PR":
        subject = f"Editorial Collaboration Opportunity for {website}"
        body = f"""Hello,

I came across {website} and wanted to explore a potential editorial collaboration.

I would love to learn about your editorial guidelines and opportunities for relevant content contributions.

Would you be open to discussing this?

Best regards"""

    elif contact_type == "Editor":
        subject = f"Guest Article Contribution for {website}"
        body = f"""Hello,

I am reaching out to explore a possible guest article contribution for {website}.

I can provide original, relevant and well-researched content that aligns with your editorial standards.

Could you please share your guest posting guidelines?

Best regards"""

    elif contact_type == "Advertising":
        subject = f"Partnership Inquiry for {website}"
        body = f"""Hello,

I would like to explore potential advertising or content partnership opportunities with {website}.

Could you please share your available options and requirements?

Best regards"""

    elif contact_type == "General Contact":
        subject = f"Content Collaboration Inquiry for {website}"
        body = f"""Hello,

I am interested in exploring a content collaboration opportunity with {website}.

Could you please direct me to the appropriate editor or person responsible for content submissions?

Thank you.

Best regards"""

    else:
        subject = f"Editorial Inquiry for {website}"
        body = f"""Hello,

I would like to learn more about content contribution opportunities at {website}.

Could you please direct me to the relevant contact person?

Best regards"""

    return {
        "email": email,
        "website": website,
        "contact_type": contact_type,
        "priority": priority,
        "subject": subject,
        "body": body,
        "approval_status": "Pending Review"
    }


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        contacts = list(csv.DictReader(file))

    results = []

    for contact in contacts:
        priority = contact.get("outreach_priority", "").strip().lower()
        ready = contact.get("outreach_ready", "").strip().lower()

        if priority not in ("high", "medium"):
            continue

        if ready != "yes":
            continue

        results.append(generate_email(contact))

    fieldnames = [
        "email",
        "website",
        "contact_type",
        "priority",
        "subject",
        "body",
        "approval_status"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(results)

    print("=" * 55)
    print("LINKBUILD AI - OUTREACH GENERATOR")
    print("=" * 55)
    print(f"Total contacts: {len(contacts)}")
    print(f"Drafts generated: {len(results)}")
    print("Emails sent: 0")
    print("Approval required: Yes")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 55)


if __name__ == "__main__":
    main()
