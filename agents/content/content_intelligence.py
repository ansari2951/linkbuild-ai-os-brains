import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "private" / "content_intelligence"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "content_input.csv"
OUTPUT_FILE = DATA_DIR / "content_analysis.csv"


def analyze_content(record):

    title = (record.get("title") or "").strip()
    niche = (record.get("niche") or "").strip()
    keyword = (record.get("target_keyword") or "").strip()
    anchor = (record.get("anchor_text") or "").strip()
    target_url = (record.get("target_url") or "").strip()
    content_type = (record.get("content_type") or "Guest Post").strip()

    issues = []

    if not title:
        issues.append("Missing title")

    if not niche:
        issues.append("Missing niche")

    if not keyword:
        issues.append("Missing target keyword")

    if not anchor:
        issues.append("Missing anchor text")

    if not target_url:
        issues.append("Missing target URL")

    if anchor and keyword:
        if anchor.lower() == keyword.lower():
            anchor_type = "EXACT_MATCH"
        elif keyword.lower() in anchor.lower():
            anchor_type = "PARTIAL_MATCH"
        else:
            anchor_type = "BRANDED_OR_OTHER"
    else:
        anchor_type = "NEEDS_REVIEW"

    return {
        **record,
        "content_type": content_type,
        "anchor_type": anchor_type,
        "review_status": "NEEDS_REVIEW" if issues else "READY_FOR_HUMAN_REVIEW",
        "issues": "; ".join(issues)
    }


def run_analysis():

    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("No content records found.")
        return

    results = [analyze_content(record) for record in records]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Analyzed {len(results)} content records.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_analysis()