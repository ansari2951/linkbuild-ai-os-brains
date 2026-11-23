
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[3]

SEO_MODULES = [
    {
        "name": "Keyword Intelligence",
        "file": "agents/seo/keyword_intelligence.py",
        "needs_url": False,
    },
    {
        "name": "Site Audit",
        "file": "agents/seo/audit/site_audit.py",
        "needs_url": True,
    },
    {
        "name": "Competitor Intelligence",
        "file": "agents/seo/competitor/competitor_intelligence.py",
        "needs_url": False,
    },
    {
        "name": "Content Gap",
        "file": "agents/seo/content_gap/content_gap_intelligence.py",
        "needs_url": False,
    },
    {
        "name": "Website Crawler",
        "file": "agents/seo/crawler/site_crawler.py",
        "needs_url": True,
    },
    {
        "name": "Image Intelligence",
        "file": "agents/seo/images/image_intelligence.py",
        "needs_url": True,
    },
    {
        "name": "Indexing Intelligence",
        "file": "agents/seo/indexing/indexing_intelligence.py",
        "needs_url": True,
    },
    {
        "name": "Internal Link Intelligence",
        "file": "agents/seo/internal_links/internal_link_intelligence.py",
        "needs_url": True,
    },
    {
        "name": "Keyword Clustering",
        "file": "agents/seo/keyword_clustering/keyword_clustering.py",
        "needs_url": False,
    },
    {
        "name": "Core Web Vitals",
        "file": "agents/seo/performance/core_web_vitals.py",
        "needs_url": True,
    },
    {
        "name": "Redirect Intelligence",
        "file": "agents/seo/redirects/redirect_intelligence.py",
        "needs_url": True,
    },
    {
        "name": "Schema Intelligence",
        "file": "agents/seo/schema/schema_intelligence.py",
        "needs_url": True,
    },
]


def validate_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must start with http:// or https://")

    if not parsed.hostname:
        raise ValueError("A valid website hostname is required.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")

    return url


def run_module(module, website_url):
    script_path = PROJECT_ROOT / module["file"]

    if not script_path.is_file():
        return {
            "module": module["name"],
            "status": "FILE_MISSING",
            "error": str(script_path),
        }

    user_input = website_url + "\n" if module["needs_url"] else ""

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=user_input,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=300,
            check=False,
        )

        status = (
            "COMPLETED"
            if result.returncode == 0
            else "FAILED"
        )

        return {
            "module": module["name"],
            "status": status,
            "return_code": result.returncode,
            "output": result.stdout[-4000:],
            "error": result.stderr[-2000:],
        }

    except subprocess.TimeoutExpired:
        return {
            "module": module["name"],
            "status": "TIMEOUT",
            "error": "Module exceeded 300 seconds.",
        }

    except Exception as error:
        return {
            "module": module["name"],
            "status": "ERROR",
            "error": str(error),
        }


def main():
    parser = argparse.ArgumentParser(
        description="LINKBUILD AI OS Central SEO Agent Runner"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Website URL to analyze",
    )
    args = parser.parse_args()

    try:
        website_url = validate_url(args.url)
    except ValueError as error:
        print("Invalid URL:", error)
        return 1

    results = []

    print("\nLINKBUILD AI OS - SEO RUNNER")
    print("Website:", website_url)
    print("=" * 55)

    for module in SEO_MODULES:
        print("\nRunning:", module["name"])

        result = run_module(module, website_url)
        results.append(result)

        print("Status:", result["status"])

    output_dir = (
        PROJECT_ROOT
        / "data"
        / "private"
        / "seo"
        / "central_runner"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    report_file = output_dir / f"seo_run_{timestamp}.json"

    report = {
        "website": website_url,
        "started_or_completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_modules": len(results),
        "completed": sum(
            item["status"] == "COMPLETED"
            for item in results
        ),
        "failed": sum(
            item["status"] != "COMPLETED"
            for item in results
        ),
        "results": results,
    }

    report_file.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8",
    )

    print("\n" + "=" * 55)
    print("SEO RUN FINISHED")
    print("Completed:", report["completed"])
    print("Failed:", report["failed"])
    print("Report:", report_file)

    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
