
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "seo"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "keywords_input.csv"
OUTPUT_FILE = DATA_DIR / "keyword_analysis.csv"



INTENT_RULES = {
    "INFORMATIONAL": [
        "what is", "how to", "guide", "tips", "benefits",
        "why", "examples", "meaning", "tutorial"
    ],
    "COMMERCIAL": [
        "best", "top", "review", "vs", "comparison",
        "alternative", "recommended"
    ],
    "TRANSACTIONAL": [
        "buy", "purchase", "price", "cost", "hire",
        "service", "order", "discount", "cheap",
        "hosting plans", "register domain"
    ],
    "NAVIGATIONAL": [
        "login", "official", "contact"
    ]
}



def detect_intent(keyword):
    text = keyword.lower()

    for intent, phrases in INTENT_RULES.items():
        if any(phrase in text for phrase in phrases):
            return intent

    return "UNCLASSIFIED"


def parse_metric(value, metric_type):
    value = (value or "").strip()

    if not value:
        return None, "MISSING"

    try:
        number = float(value)

        if number < 0:
            return None, "INVALID"

        if metric_type == "volume":
            if not number.is_integer():
                return None, "INVALID"
            return int(number), "VALID"

        if metric_type == "difficulty":
            if number > 100:
                return None, "INVALID"
            return number, "VALID"

    except (ValueError, TypeError):
        return None, "INVALID"

    return None, "INVALID"


def analyze_keyword(record):
    keyword = (record.get("keyword") or "").strip()
    niche = (record.get("niche") or "").strip()

    volume, volume_status = parse_metric(
        record.get("search_volume"), "volume"
    )

    difficulty, difficulty_status = parse_metric(
        record.get("keyword_difficulty"), "difficulty"
    )

    intent = detect_intent(keyword)

    if not keyword:
        opportunity = "NEEDS_REVIEW"
        metric_status = "NEEDS_REVIEW"

    elif "INVALID" in (volume_status, difficulty_status):
        opportunity = "NEEDS_REVIEW"
        metric_status = "INVALID_METRICS"

    elif volume is None or difficulty is None:
        opportunity = "NEEDS_DATA"
        metric_status = "MISSING_METRICS"

    else:
        metric_status = "COMPLETE"

        if volume >= 1000 and difficulty <= 30:
            opportunity = "HIGH"
        elif volume >= 300 and difficulty <= 50:
            opportunity = "MEDIUM"
        else:
            opportunity = "LOW"

    return {
        "keyword": keyword,
        "niche": niche,
        "search_volume": volume if volume is not None else "",
        "keyword_difficulty": difficulty if difficulty is not None else "",
        "search_intent": intent,
        "metric_status": metric_status,
        "opportunity": opportunity,
        "review_status": (
            "NEEDS_REVIEW" if not keyword else "READY_FOR_REVIEW"
        )
    }


def run_analysis():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No keywords found.")
        return

    results = [analyze_keyword(row) for row in records]

    fieldnames = [
        "keyword",
        "niche",
        "search_volume",
        "keyword_difficulty",
        "search_intent",
        "metric_status",
        "opportunity",
        "review_status"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Analyzed {len(results)} keywords.")
    print(f"Results saved to: {OUTPUT_FILE}")

    missing = sum(
        1 for row in results
        if row["metric_status"] == "MISSING_METRICS"
    )

    invalid = sum(
        1 for row in results
        if row["metric_status"] == "INVALID_METRICS"
    )

    print(f"Keywords needing metrics: {missing}")
    print(f"Keywords with invalid metrics: {invalid}")


if __name__ == "__main__":
    run_analysis()
