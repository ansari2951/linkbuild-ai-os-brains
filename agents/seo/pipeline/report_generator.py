
from pathlib import Path
import csv
from datetime import datetime


ROOT_DIR = Path(__file__).resolve().parents[3]

REPORT_DIR = ROOT_DIR / "data/private/seo/pipeline"
OUTPUT_FILE = REPORT_DIR / "consolidated_seo_report.csv"

REPORT_SOURCES = {
    "Site Audit": "data/private/seo/audits/site_audit_results.csv",
    "Website Crawler": "data/private/seo/crawler/crawl_results.csv",
    "Image Intelligence": "data/private/seo/images/image_audit.csv",
    "Indexing": "data/private/seo/indexing/indexing_report.csv",
    "Internal Links": "data/private/seo/internal_links/internal_link_audit.csv",
    "Core Web Vitals": "data/private/seo/performance/core_web_vitals.csv",
    "Redirects": "data/private/seo/redirects/redirect_results.csv",
    "Schema": "data/private/seo/schema/schema_results.csv",
    "Keyword Intelligence": "data/private/seo/keyword_analysis.csv",
    "Competitor Intelligence": "data/private/seo/competitors/competitor_analysis.csv",
    "Content Gap": "data/private/seo/content_gap/content_gap_report.csv",
    "Keyword Clustering": "data/private/seo/keyword_clustering/keyword_clusters.csv",
}


def collect_reports():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    all_rows = []
    source_status = []

    for module_name, relative_path in REPORT_SOURCES.items():
        file_path = ROOT_DIR / relative_path

        if not file_path.exists():
            source_status.append({
                "module": module_name,
                "status": "OUTPUT_NOT_FOUND"
            })
            continue

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8-sig",
                newline=""
            ) as file:
                reader = csv.DictReader(file)

                if not reader.fieldnames:
                    source_status.append({
                        "module": module_name,
                        "status": "EMPTY_FILE"
                    })
                    continue

                count = 0

                for row in reader:
                    all_rows.append({
                        "module": module_name,
                        "source_file": relative_path,
                        "collected_at": datetime.now().isoformat(),
                        "data": str(row)
                    })
                    count += 1

                source_status.append({
                    "module": module_name,
                    "status": "COLLECTED",
                    "rows": count
                })

        except Exception as error:
            source_status.append({
                "module": module_name,
                "status": "READ_ERROR",
                "error": str(error)
            })

    fieldnames = [
        "module",
        "source_file",
        "collected_at",
        "data"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nCONSOLIDATED SEO REPORT")
    print("=" * 35)

    for item in source_status:
        print(f"{item['module']}: {item['status']}")

    print(f"\nTotal collected rows: {len(all_rows)}")
    print(f"Report saved: {OUTPUT_FILE}")

    return {
        "output_file": str(OUTPUT_FILE),
        "total_rows": len(all_rows),
        "sources": source_status
    }


if __name__ == "__main__":
    collect_reports()
