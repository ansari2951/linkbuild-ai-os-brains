
import csv
import re
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "private" / "email_extraction"

INPUT_FILE = DATA_DIR / "outreach_drafts.csv"
OUTPUT_FILE = DATA_DIR / "personalized_outreach.csv"


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def get_website_name(url):
    url = clean_text(url)

    if not url:
        return "your website"

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    domain = urlparse(url).netloc.lower()
    domain = domain.replace("www.", "")

    if not domain:
        return "your website"

    return domain.split(".")[0].replace("-", " ").title()


def create_personalized_email(draft):
    website = clean_text(draft.get("website"))
    website_name = get_website_name(website)

    contact_type = clean_text(
        draft.get("contact_type")
    ).lower()

    original_subject = clean_text(
        draft.get("subject")
    )

    original_body = clean_text(
        draft.get("body")
    )

    if "press" in contact_type:
        greeting = "Hello Press Team"
        subject = f"Content Collaboration with {website_name}"
    elif "advertising" in contact_type:
        greeting = "Hello Advertising Team"
        subject = f"Advertising and Content Partnership"
    elif "editor" in contact_type:
        greeting = "Hello Editorial Team"
        subject = f"Editorial Collaboration Opportunity"
    else:
        greeting = "Hello Team"
        subject = f"Content Collaboration Opportunity"

    body = (
        f"{greeting},\n\n"
        f"I hope you're doing well.\n\n"
        f"I came across {website_name} and wanted to "
        f"reach out regarding a potential content collaboration.\n\n"
        f"We work with websites and publishers on relevant "
        f"guest contributions and editorial content. "
        f"I'd be happy to explore whether there is an opportunity "
        f"to contribute content that fits your audience.\n\n"
        f"Could you please share your guidelines and "
        f"collaboration requirements?\n\n"
        f"Thank you for your time.\n\n"
        f"Best regards"
    )

    return {
        "email": clean_text(draft.get("email")),
        "website": website,
        "website_name": website_name,
        "contact_type": clean_text(draft.get("contact_type")),
        "subject": subject or original_subject,
        "body": body,
        "original_subject": original_subject,
        "original_body": original_body,
        "approval_status": "PENDING",
    }


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(
        INPUT_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        drafts = list(csv.DictReader(file))

    if not drafts:
        print("No outreach drafts found.")
        return

    personalized = [
        create_personalized_email(draft)
        for draft in drafts
    ]

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=personalized[0].keys()
        )
        writer.writeheader()
        writer.writerows(personalized)

    print("Personalization drafts generated.")
    print(f"Total drafts: {len(personalized)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
