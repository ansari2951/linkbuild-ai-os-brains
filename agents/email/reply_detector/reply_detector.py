
import csv
import re
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "private" / "email_extraction"

INPUT_FILE = DATA_DIR / "publisher_replies.csv"
OUTPUT_FILE = DATA_DIR / "classified_replies.csv"

CATEGORIES = {
    "POSITIVE": [
        "interested", "sounds good", "happy to",
        "we can publish", "send details", "let's proceed",
        "sure", "yes", "welcome"
    ],
    "PRICE_NEGOTIATION": [
        "price", "cost", "fee", "rate", "budget",
        "discount", "payment", "charge", "expensive"
    ],
    "NEGATIVE": [
        "not interested", "cannot publish", "can't publish",
        "do not accept", "don't accept", "not possible",
        "declined", "no thanks"
    ],
    "CONTENT_REQUEST": [
        "send article", "send content", "share the article",
        "guidelines", "word count", "topic",
        "draft", "content requirements"
    ],
    "FOLLOW_UP": [
        "follow up", "checking in", "any update",
        "reminder", "waiting for your response"
    ]
}


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def classify_reply(message):
    text = clean_text(message).lower()

    if not text:
        return "EMPTY"

    scores = {}

    for category, keywords in CATEGORIES.items():
        scores[category] = sum(
            1 for keyword in keywords if keyword in text
        )

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "NEEDS_REVIEW"

    # Conflicting signals should be reviewed manually.
    matched = [
        category for category, score in scores.items()
        if score > 0
    ]

    if len(matched) > 1:
        return "NEEDS_REVIEW"

    return best_category


def process_reply(reply):
    message = clean_text(reply.get("message"))
    category = classify_reply(message)

    return {
        "sender_email": clean_text(reply.get("sender_email")),
        "subject": clean_text(reply.get("subject")),
        "message": message,
        "category": category,
        "received_at": clean_text(reply.get("received_at")),
        "processed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "action_required": (
            "YES" if category != "EMPTY" else "NO"
        )
    }


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        print("Expected columns: sender_email, subject, message, received_at")
        return

    with open(
        INPUT_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        required = {"sender_email", "subject", "message"}

        if not required.issubset(reader.fieldnames or []):
            print("Required CSV columns are missing.")
            return

        replies = list(reader)

    if not replies:
        print("No replies found.")
        return

    results = [process_reply(reply) for reply in replies]

    DATA_DIR.mkdir(parents=True, exist_ok=True)

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

    print("Reply classification file generated.")
    print(f"Total replies: {len(results)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
