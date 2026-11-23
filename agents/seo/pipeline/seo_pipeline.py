
from pathlib import Path
import sys
import csv

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.seo.pipeline.input_validator import validate_input_file
from agents.seo.pipeline.pipeline_config import (
    INPUT_FILE,
    REPORT_DIR,
    STATUS_REPORT
)
from agents.seo.pipeline.agent_runner import run_all
from agents.seo.pipeline.execution_logger import (
    start_run,
    log_event,
    finish_run
)
from agents.seo.pipeline.error_handler import record_error
from agents.seo.pipeline.report_generator import collect_reports


def save_status_report(results):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = ["module", "website", "status"]

    with open(
        STATUS_REPORT,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                field: result.get(field, "")
                for field in fieldnames
            })

    print(f"\nStatus report saved: {STATUS_REPORT}")


def run_pipeline():
    print("\nLINKBUILD AI OS SEO PIPELINE")
    print("=" * 45)

    run_id = None

    try:
        run_id = start_run()

        valid_urls, rejected_urls = validate_input_file()

        print(f"\nValid websites: {len(valid_urls)}")
        print(f"Rejected websites: {len(rejected_urls)}")

        if not valid_urls:
            print("\nNo valid websites found. Pipeline stopped.")

            log_event(run_id, "PIPELINE_STOPPED", {
                "reason": "No valid websites",
                "rejected_websites": rejected_urls
            })

            finish_run(run_id, "STOPPED", {
                "reason": "No valid websites"
            })

            return 1

        print("\nStarting SEO modules...")

        execution_report = run_all(valid_urls)
        results = execution_report["results"]

        save_status_report(results)

        print("\nGenerating consolidated report...")

        try:
            collect_reports()
        except Exception as error:
            print(f"Report generation issue: {error}")

            record_error(
                error,
                module_name="report_generator",
                run_id=run_id,
                context={"message": "Report generation failed"}
            )

        final_status = (
            "COMPLETED"
            if execution_report["failed"] == 0
            else "FAILED"
        )

        log_event(run_id, "PIPELINE_COMPLETED", {
            "websites": valid_urls,
            "completed": execution_report["completed"],
            "failed": execution_report["failed"]
        })

        finish_run(run_id, final_status, {
            "websites": valid_urls,
            "completed": execution_report["completed"],
            "failed": execution_report["failed"]
        })

        print("\nSEO PIPELINE FINISHED")
        print(f"Completed: {execution_report['completed']}")
        print(f"Failed: {execution_report['failed']}")

        return 0 if execution_report["failed"] == 0 else 1

    except Exception as error:
        print(f"\nPIPELINE ERROR: {error}")

        if run_id is not None:
            log_event(run_id, "PIPELINE_ERROR", {
                "error": str(error)
            })

            finish_run(run_id, "FAILED", {
                "error": str(error)
            })

        record_error(
            error,
            module_name="seo_pipeline",
            run_id=run_id,
            context={"message": "SEO pipeline failed"}
        )

        return 1


if __name__ == "__main__":
    sys.exit(run_pipeline())
