
from pathlib import Path
import subprocess
import sys
import json
from datetime import datetime

from agents.seo.pipeline.pipeline_config import ENABLED_MODULES


ROOT_DIR = Path(__file__).resolve().parents[3]

SEO_MODULES = [
    {
        "name": "Site Audit",
        "file": "agents/seo/audit/site_audit.py",
        "needs_url": True
    },
    {
        "name": "Website Crawler",
        "file": "agents/seo/crawler/site_crawler.py",
        "needs_url": True
    },
    {
        "name": "Image Intelligence",
        "file": "agents/seo/images/image_intelligence.py",
        "needs_url": True
    },
    {
        "name": "Indexing Intelligence",
        "file": "agents/seo/indexing/indexing_intelligence.py",
        "needs_url": True
    },
    {
        "name": "Internal Link Analysis",
        "file": "agents/seo/internal_links/internal_link_intelligence.py",
        "needs_url": True
    },
    {
        "name": "Core Web Vitals",
        "file": "agents/seo/performance/core_web_vitals.py",
        "needs_url": True
    },
    {
        "name": "Redirect Analysis",
        "file": "agents/seo/redirects/redirect_intelligence.py",
        "needs_url": True
    },
    {
        "name": "Schema Analysis",
        "file": "agents/seo/schema/schema_intelligence.py",
        "needs_url": True
    },
    {
        "name": "Keyword Intelligence",
        "file": "agents/seo/keyword_intelligence.py",
        "needs_url": False,
        "inputs": ["data/private/seo/keywords_input.csv"]
    },
    {
        "name": "Competitor Intelligence",
        "file": "agents/seo/competitor/competitor_intelligence.py",
        "needs_url": False,
        "inputs": ["data/private/seo/competitors/competitors_input.csv"]
    },
    {
        "name": "Content Gap Analysis",
        "file": "agents/seo/content_gap/content_gap_intelligence.py",
        "needs_url": False,
        "inputs": [
            "data/private/seo/content_gap/own_keywords.csv",
            "data/private/seo/content_gap/competitor_keywords.csv"
        ]
    },
    {
        "name": "Keyword Clustering",
        "file": "agents/seo/keyword_clustering/keyword_clustering.py",
        "needs_url": False,
        "inputs": [
            "data/private/seo/keyword_clustering/keywords_input.csv"
        ]
    }
]

MODULE_CONFIG_KEYS = {
    "Site Audit": "site_audit",
    "Website Crawler": "crawler",
    "Image Intelligence": "images",
    "Indexing Intelligence": "indexing",
    "Internal Link Analysis": "internal_links",
    "Core Web Vitals": "core_web_vitals",
    "Redirect Analysis": "redirects",
    "Schema Analysis": "schema",
    "Keyword Intelligence": "keyword_intelligence",
    "Competitor Intelligence": "competitor_intelligence",
    "Content Gap Analysis": "content_gap",
    "Keyword Clustering": "keyword_clustering",
}

def run_module(module, website_url=None):
    script_path = ROOT_DIR / module["file"]

    if not script_path.exists():
        return {
            "module": module["name"],
            "website": website_url,
            "status": "NOT_FOUND"
        }

    for input_file in module.get("inputs", []):
        if not (ROOT_DIR / input_file).exists():
            return {
                "module": module["name"],
                "website": website_url,
                "status": "SKIPPED",
                "message": f"Missing input: {input_file}"
            }

    user_input = f"{website_url}\n" if module["needs_url"] else ""

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=user_input,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=ROOT_DIR
        )

        return {
            "module": module["name"],
            "website": website_url,
            "status": "COMPLETED" if result.returncode == 0 else "FAILED",
            "return_code": result.returncode,
            "output": result.stdout[-3000:],
            "error": result.stderr[-2000:]
        }

    except subprocess.TimeoutExpired:
        return {
            "module": module["name"],
            "website": website_url,
            "status": "TIMEOUT"
        }

    except Exception as error:
        return {
            "module": module["name"],
            "website": website_url,
            "status": "ERROR",
            "message": str(error)
        }



def run_all(website_urls):
    results = []

    for website_url in website_urls:
        print(f"\nStarting website analysis: {website_url}")

        for module in SEO_MODULES:
            if not module["needs_url"]:
                continue

            config_key = MODULE_CONFIG_KEYS[module["name"]]

            if not ENABLED_MODULES.get(config_key, False):
                print(f"Disabled: {module['name']}")
                results.append({
                    "module": module["name"],
                    "website": website_url,
                    "status": "DISABLED"
                })
                continue

            print(f"Running: {module['name']}")
            result = run_module(module, website_url)
            results.append(result)
            print(f"Status: {result['status']}")

    print("\nRunning CSV-based SEO modules...")

    for module in SEO_MODULES:
        if module["needs_url"]:
            continue

        config_key = MODULE_CONFIG_KEYS[module["name"]]

        if not ENABLED_MODULES.get(config_key, False):
            print(f"Disabled: {module['name']}")
            results.append({
                "module": module["name"],
                "website": None,
                "status": "DISABLED"
            })
            continue

        print(f"Running: {module['name']}")
        result = run_module(module)
        results.append(result)
        print(f"Status: {result['status']}")

    output_dir = ROOT_DIR / "data/private/seo/central_runner"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"seo_run_{timestamp}.json"

    report = {
        "project": "LINKBUILD AI OS",
        "run_time": datetime.now().isoformat(),
        "websites": website_urls,
        "total_modules": len(results),
        "completed": sum(r["status"] == "COMPLETED" for r in results),
        "failed": sum(
            r["status"] in ["FAILED", "ERROR", "TIMEOUT", "NOT_FOUND"]
            for r in results
        ),
        "skipped": sum(r["status"] == "SKIPPED" for r in results),
        "disabled": sum(r["status"] == "DISABLED" for r in results),
        "results": results
    }

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print(f"\nExecution report saved: {output_file}")
    return report
