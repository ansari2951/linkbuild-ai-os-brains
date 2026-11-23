import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_DIR = PROJECT_ROOT / "data" / "private" / "website_quality"
INPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = INPUT_DIR / "websites_input.csv"
OUTPUT_FILE = INPUT_DIR / "website_quality_results.csv"


def calculate_quality(website):

    dr = float(website.get("dr") or 0)
    da = float(website.get("da") or 0)
    traffic = int(float(website.get("traffic") or 0))
    spam_score = float(website.get("spam_score") or 0)

    score = 0

    # Domain Rating
    if dr >= 50:
        score += 25
    elif dr >= 30:
        score += 18
    elif dr >= 15:
        score += 10
    elif dr > 0:
        score += 5

    # Domain Authority
    if da >= 50:
        score += 25
    elif da >= 30:
        score += 18
    elif da >= 15:
        score += 10
    elif da > 0:
        score += 5

    # Organic traffic
    if traffic >= 50000:
        score += 25
    elif traffic >= 10000:
        score += 20
    elif traffic >= 3000:
        score += 15
    elif traffic >= 500:
        score += 10
    elif traffic > 0:
        score += 5

    # Spam score
    if spam_score <= 5:
        score += 25
    elif spam_score <= 10:
        score += 15
    elif spam_score <= 20:
        score += 5

    if score >= 80:
        rating = "HIGH"
    elif score >= 55:
        rating = "MEDIUM"
    else:
        rating = "LOW"

    return {
        "quality_score": score,
        "quality_rating": rating
    }


def analyze_websites():

    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
        websites = list(csv.DictReader(file))

    results = []

    for website in websites:
        quality = calculate_quality(website)

        results.append({
            **website,
            **quality
        })

    if not results:
        print("No websites found in input file.")
        return

    fieldnames = list(results[0].keys())

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Analyzed {len(results)} websites.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    analyze_websites()