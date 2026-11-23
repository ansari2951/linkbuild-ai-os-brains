
from pathlib import Path
import csv
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "pipeline"
)

OUTPUT_FILE = OUTPUT_DIR / "consolidated_seo_report.csv"

REPORT_SOURCES = {
    "site_audit": (
        "data/private/seo/audits/site_audit_results.csv"
    ),
    "crawler": (
        "data/private/seo/crawler/crawl_results.csv"
    ),
    "indexing": (
        "data/private/seo/indexing/indexing_report.csv"
    ),
    "schema": (
        "data/private/seo/schema/schema_results.csv"
    ),
    "redirects": (
        "data/private/seo/redirects/redirect_results.csv"
    ),
    "core_web_vitals": (
        "data/private/seo/performance/core_web_vitals.csv"
    ),
    "images": (
        "data/private/seo/images/image_audit.csv"
    ),
    "internal_links": (
        "data/private/seo/internal_links/internal_link_report.csv"
    ),
    "keyword_clustering": (
        "data/private/seo/keyword_clustering/keyword_clusters.csv"
    ),
    "content_gap": (
        "data/private/seo/content_gap/content_gap_report.csv"
    ),
}


def read_csv_report(report_path):
    if not report_path.exists():
        return []

    try:
        with open(
            report_path,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            return list(csv.DictReader(file))

    except (OSError, csv.Error, UnicodeError) as error:
        print(f"Could not read {report_path.name}: {error}")
        return []


def collect_reports():
    combined_rows = []

    for module_name, relative_path in REPORT_SOURCES.items():
        report_path = PROJECT_ROOT / relative_path
        records = read_csv_report(report_path)

        if not records:
            combined_rows.append({
                "module": module_name,
                "source_file": relative_path,
                "record_number": "",
                "record_data": "No records available",
                "collected_at": datetime.now().isoformat(
                    timespec="seconds"
                ),
            })
            continue

        for number, record in enumerate(records, start=1):
            combined_rows.append({
                "module": module_name,
                "source_file": relative_path,
                "record_number": number,
                "record_data": str(record),
                "collected_at": datetime.now().isoformat(
                    timespec="seconds"
                ),
            })

    return combined_rows


def save_report(rows):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "module",
        "source_file",
        "record_number",
        "record_data",
        "collected_at",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate_report():
    rows = collect_reports()
    save_report(rows)

    print("\n===== CONSOLIDATED SEO REPORT =====")
    print(f"Modules checked: {len(REPORT_SOURCES)}")
    print(f"Total report records: {len(rows)}")
    print(f"Report saved at: {OUTPUT_FILE}")

    return rows


if __name__ == "__main__":
    generate_report()
