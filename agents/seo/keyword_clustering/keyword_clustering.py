
import csv
import re
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "keyword_clustering"
)

INPUT_FILE = INPUT_DIR / "keywords_input.csv"
OUTPUT_FILE = INPUT_DIR / "keyword_clusters.csv"

MIN_SHARED_WORDS = 2

STOP_WORDS = {
    "a", "an", "the", "is", "are", "for", "to",
    "of", "in", "on", "with", "and", "or", "by",
    "how", "what", "best", "top"
}


def normalize_keyword(keyword):
    keyword = keyword.lower().strip()
    keyword = re.sub(r"[^a-z0-9\s]", " ", keyword)
    return " ".join(keyword.split())


def tokenize(keyword):
    words = normalize_keyword(keyword).split()

    return {
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    }


def detect_intent(keyword):
    keyword = keyword.lower()

    informational = [
        "how", "what", "why", "guide",
        "tips", "tutorial", "meaning"
    ]

    commercial = [
        "best", "top", "review",
        "comparison", "vs", "services"
    ]

    transactional = [
        "buy", "price", "cost",
        "hire", "order", "purchase"
    ]

    navigational = [
        "login", "website", "official"
    ]

    if any(word in keyword.split() for word in transactional):
        return "Transactional"

    if any(word in keyword.split() for word in commercial):
        return "Commercial"

    if any(word in keyword.split() for word in navigational):
        return "Navigational"

    if any(word in keyword.split() for word in informational):
        return "Informational"

    return "Unknown"


def read_keywords():
    if not INPUT_FILE.exists():
        print(f"Input file missing: {INPUT_FILE}")
        return []

    keywords = []

    with open(
        INPUT_FILE,
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

            keywords.append({
                "keyword": keyword,
                "tokens": tokenize(keyword),
                "search_volume": row.get("search_volume", "0"),
                "intent": detect_intent(keyword)
            })

    return keywords


def calculate_similarity(tokens_a, tokens_b):
    if not tokens_a or not tokens_b:
        return 0

    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b

    return len(intersection) / len(union)


def create_clusters(keywords):
    clusters = []

    for item in keywords:
        assigned = False

        for cluster in clusters:
            representative = cluster[0]

            shared_words = (
                item["tokens"] & representative["tokens"]
            )

            similarity = calculate_similarity(
                item["tokens"],
                representative["tokens"]
            )

            if (
                len(shared_words) >= MIN_SHARED_WORDS
                or similarity >= 0.5
            ):
                cluster.append(item)
                assigned = True
                break

        if not assigned:
            clusters.append([item])

    return clusters


def save_clusters(clusters):
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []

    for cluster_number, cluster in enumerate(
        clusters,
        start=1
    ):
        primary_keyword = max(
            cluster,
            key=lambda item: len(item["tokens"])
        )["keyword"]

        for item in cluster:
            rows.append({
                "cluster_id": cluster_number,
                "primary_keyword": primary_keyword,
                "keyword": item["keyword"],
                "search_volume": item["search_volume"],
                "search_intent": item["intent"],
                "cluster_size": len(cluster)
            })

    if not rows:
        print("No keyword clusters created.")
        return

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Keyword clusters saved: {OUTPUT_FILE}")


def main():
    keywords = read_keywords()

    if not keywords:
        print("Add keywords to the input CSV first.")
        return

    clusters = create_clusters(keywords)
    save_clusters(clusters)

    print("\nKeyword Clustering Summary")
    print("Total keywords:", len(keywords))
    print("Total clusters:", len(clusters))


if __name__ == "__main__":
    main()
