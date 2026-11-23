
import csv
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "content_gap"
)

OUTPUT_DIR = INPUT_DIR
OUTPUT_FILE = OUTPUT_DIR / "content_gap_report.csv"

OWN_KEYWORDS_FILE = INPUT_DIR / "own_keywords.csv"
COMPETITOR_KEYWORDS_FILE = INPUT_DIR / "competitor_keywords.csv"


def normalize_keyword(keyword):
    return " ".join(keyword.lower().strip().split())


def read_keywords(file_path):
    keywords = {}

    if not file_path.exists():
        print(f"Input file missing: {file_path}")
        return keywords

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            keyword = normalize_keyword(
                row.get("keyword", "")
            )

            if not keyword:
                continue

            try:
                volume = int(row.get("search_volume", 0) or 0)
            except (ValueError, TypeError):
                volume = 0

            try:
                difficulty = float(
                    row.get("keyword_difficulty", 0) or 0
                )
            except (ValueError, TypeError):
                difficulty = 0

            keywords[keyword] = {
                "search_volume": volume,
                "keyword_difficulty": difficulty,
                "intent": row.get("intent", "Unknown"),
                "url": row.get("url", "")
            }

    return keywords


def calculate_opportunity(volume, difficulty):
    volume_score = min(volume / 100, 100)
    difficulty_score = max(0, 100 - difficulty)

    score = (
        volume_score * 0.60
        + difficulty_score * 0.40
    )

    return round(score, 2)


def classify_opportunity(score):
    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def analyze_content_gap(own_keywords, competitor_keywords):
    results = []

    for keyword, competitor_data in competitor_keywords.items():

        own_data = own_keywords.get(keyword)

        if own_data:
            status = "ALREADY_TARGETED"
        else:
            status = "CONTENT_GAP"

        volume = competitor_data["search_volume"]
        difficulty = competitor_data["keyword_difficulty"]

        score = calculate_opportunity(
            volume,
            difficulty
        )

        results.append({
            "keyword": keyword,
            "status": status,
            "search_volume": volume,
            "keyword_difficulty": difficulty,
            "search_intent": competitor_data["intent"],
            "competitor_url": competitor_data["url"],
            "opportunity_score": score,
            "priority": classify_opportunity(score)
        })

    results.sort(
        key=lambda item: item["opportunity_score"],
        reverse=True
    )

    return results


def save_report(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not results:
        print("No content gap data available.")
        return

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"Content gap report saved: {OUTPUT_FILE}")


def main():
    own_keywords = read_keywords(OWN_KEYWORDS_FILE)
    competitor_keywords = read_keywords(
        COMPETITOR_KEYWORDS_FILE
    )

    if not competitor_keywords:
        print("Add competitor keywords before analysis.")
        return

    results = analyze_content_gap(
        own_keywords,
        competitor_keywords
    )

    save_report(results)

    gaps = [
        item for item in results
        if item["status"] == "CONTENT_GAP"
    ]

    print("\nContent Gap Summary")
    print("Your keywords:", len(own_keywords))
    print("Competitor keywords:", len(competitor_keywords))
    print("Missing keyword opportunities:", len(gaps))
    print(
        "High priority gaps:",
        sum(1 for item in gaps if item["priority"] == "HIGH")
    )


if __name__ == "__main__":
    main()
