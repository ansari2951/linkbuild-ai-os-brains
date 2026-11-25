
import csv
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "private" / "email_extraction"
DRAFTS_FILE = DATA_DIR / "outreach_drafts.csv"

# Safe defaults
SEND_EMAILS = os.getenv("SEND_EMAILS", "false").lower() == "true"

# SMTP settings must be configured as environment variables
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER") or os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
APPROVAL_FILE = DATA_DIR / "approval_decisions.csv"


def load_approved_overrides():
    overrides = {}
    if not APPROVAL_FILE.exists():
        return overrides
    try:
        with open(APPROVAL_FILE, "r", newline="", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                email = (row.get("email") or "").strip().lower()
                decision = (row.get("decision") or "").strip().upper()
                if email and decision:
                    overrides[email] = decision
    except (OSError, csv.Error):
        pass
    return overrides


def send_email(to_email, subject, body):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)


def main():
    if not DRAFTS_FILE.exists():
        print(f"Draft file not found: {DRAFTS_FILE}")
        return

    if SEND_EMAILS and not all(
        [SMTP_HOST, SMTP_USER, SMTP_PASSWORD]
    ):
        print("SMTP settings are missing. No emails sent.")
        return

    sent_count = 0
    skipped_count = 0

    with open(DRAFTS_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required = {
            "email", "subject", "body", "approval_status"
        }

        if not required.issubset(reader.fieldnames or []):
            print("Required CSV columns are missing.")
            return

        approved_overrides = load_approved_overrides()

        for draft in reader:
            email = (draft.get("email") or "").strip()
            subject = (draft.get("subject") or "").strip()
            body = (draft.get("body") or "").strip()
            status = (
                approved_overrides.get(email.lower())
                or draft.get("approval_status")
                or ""
            ).strip().upper()

            if status != "APPROVED":
                skipped_count += 1
                continue

            if not email or not subject or not body:
                print("Skipped incomplete draft.")
                skipped_count += 1
                continue

            if not SEND_EMAILS:
                print(f"[TEST ONLY] Approved draft: {email}")
                skipped_count += 1
                continue

            try:
                send_email(email, subject, body)
                print(f"[SENT] {email}")
                sent_count += 1
            except Exception as error:
                print(f"[ERROR] {email}: {error}")

    print("\n--- SENDER REPORT ---")
    print(f"Emails sent: {sent_count}")
    print(f"Skipped / test drafts: {skipped_count}")
    print(f"Sending enabled: {SEND_EMAILS}")


if __name__ == "__main__":
    main()
