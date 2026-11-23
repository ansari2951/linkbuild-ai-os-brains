
import csv
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.seo.pipeline.input_validator import validate_input_file
from agents.seo.pipeline.pipeline_config import (
    PIPELINE_NAME,
    ENABLED_MODULES,
    REPORT_DIR,
)
from agents.seo.pipeline.report_generator import generate_report
from agents.seo.pipeline.execution_logger import (
    start_run,
    log_event,
    finish_run,
)
from agents.seo.pipeline.error_handler import record_error


MODULE_FILES = {
    "crawler": "agents/seo/crawler/site_crawler.py",
    "site_audit": "agents/seo/audit/site_audit.py",
    "indexing": "agents/seo/indexing/indexing_intelligence.py",
    "schema": "agents/seo/schema/schema_intelligence.py",
    "redirects": "agents/seo/redirects/redirect_intelligence.py",
    "core_web_vitals": "agents/seo/performance/core_web_vitals.py",
    "images": "agents/seo/images/image_intelligence.py",
    "internal_links": "agents/seo/internal_links/internal_link_intelligence.py",
    "keyword_intelligence": "agents/seo/keyword_intelligence.py",
    "keyword_clustering": "agents/seo/keyword_clustering/keyword_clustering.py",
    "content_gap": "agents/seo/content_gap/content_gap_intelligence.py",
    "competitor_intelligence": "agents/seo/competitor/competitor_intelligence.py",
}

STATUS_FILE = REPORT_DIR / "seo_pipeline_status.csv"


def check_modules():
    results = []

    for name, relative_path in MODULE_FILES.items():
        enabled = ENABLED_MODULES.get(name, False)
        exists = (PROJECT_ROOT / relative_path).is_file()

        if not enabled:
            status = "DISABLED"
        elif exists:
            status = "AVAILABLE"
        else:
            status = "MISSING"

        results.append({
            "module": name,
            "file": relative_path,
            "status": status,
        })

    return results


def save_status_report(module_results, valid_urls, rejected_urls):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "record_type",
        "name",
        "status",
        "details",
        "created_at",
    ]

    timestamp = datetime.now().isoformat(timespec="seconds")

    with open(
        STATUS_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for item in module_results:
            writer.writerow({
                "record_type": "MODULE",
                "name": item["module"],
                "status": item["status"],
                "details": item["file"],
                "created_at": timestamp,
            })

        for url in valid_urls:
            writer.writerow({
                "record_type": "WEBSITE",
                "name": url,
                "status": "VALIDATED",
                "details": "Ready for a future execution stage",
                "created_at": timestamp,
            })

        for item in rejected_urls:
            writer.writerow({
                "record_type": "REJECTED_INPUT",
                "name": item["url"],
                "status": "REJECTED",
                "details": item["reason"],
                "created_at": timestamp,
            })


def run_pipeline():
    run_id = start_run()

    print(f"\n===== {PIPELINE_NAME} =====")

    try:
        log_event(run_id, "INPUT_VALIDATION_STARTED")

        valid_urls, rejected_urls = validate_input_file()

        log_event(
            run_id,
            "INPUT_VALIDATION_COMPLETED",
            {
                "valid_websites": len(valid_urls),
                "rejected_entries": len(rejected_urls),
            },
        )

        module_results = check_modules()

        available = sum(
            item["status"] == "AVAILABLE"
            for item in module_results
        )

        missing = sum(
            item["status"] == "MISSING"
            for item in module_results
        )

        disabled = sum(
            item["status"] == "DISABLED"
            for item in module_results
        )

        save_status_report(
            module_results,
            valid_urls,
            rejected_urls,
        )

        log_event(
            run_id,
            "MODULE_CHECK_COMPLETED",
            {
                "available": available,
                "missing": missing,
                "disabled": disabled,
            },
        )

        print("\n----- INPUT SUMMARY -----")
        print(f"Valid websites: {len(valid_urls)}")
        print(f"Rejected entries: {len(rejected_urls)}")

        print("\n----- MODULE SUMMARY -----")
        print(f"Available: {available}")
        print(f"Missing: {missing}")
        print(f"Disabled: {disabled}")

        for item in module_results:
            print(f'{item["module"]}: {item["status"]}')

        print(f"\nStatus report: {STATUS_FILE}")

        log_event(run_id, "REPORT_COLLECTION_STARTED")
        generate_report()
        log_event(run_id, "REPORT_COLLECTION_COMPLETED")

        finish_run(
            run_id,
            "COMPLETED",
            {
                "valid_websites": len(valid_urls),
                "rejected_entries": len(rejected_urls),
                "available_modules": available,
                "missing_modules": missing,
                "disabled_modules": disabled,
            },
        )

        print("\nPipeline preparation completed.")
        print("SEO agents have NOT been executed yet.")

    except Exception as error:
        record_error(
            error,
            module_name="seo_pipeline",
            run_id=run_id,
        )

        try:
            finish_run(
                run_id,
                "FAILED",
                {"error": str(error)},
            )
        except Exception as logging_error:
            print(f"Could not finish execution log: {logging_error}")

        print(f"\nPipeline failed: {error}")


if __name__ == "__main__":
    run_pipeline()
