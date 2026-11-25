import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = PROJECT_ROOT / "data" / "private"
PUBLIC_DIR = PROJECT_ROOT / "public"
OUTPUT_FILE = PUBLIC_DIR / "dashboard-data.json"


def _read_csv(path):
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))
    except (OSError, csv.Error):
        return []


def _read_json(path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _count_sqlite_rows(db_path, table_name):
    if not db_path.exists():
        return 0
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            ).fetchone()
            if not row:
                return 0
            return conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    except sqlite3.Error:
        return 0


def build_dashboard_data():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    from core.master_brain.registry import list_agents
    from core.brain import CentralBrain

    brain_summary = CentralBrain().get_system_summary()
    agents_registry = list_agents()

    seo_status_rows = _read_csv(PRIVATE_DIR / "seo" / "pipeline" / "seo_pipeline_status.csv")
    seo_completed = sum(1 for r in seo_status_rows if r.get("status") == "COMPLETED")
    seo_failed = sum(1 for r in seo_status_rows if r.get("status") == "FAILED")

    seo_runs = sorted((PRIVATE_DIR / "seo" / "central_runner").glob("seo_run_*.json"))
    latest_seo_run = _read_json(seo_runs[-1], {}) if seo_runs else {}

    publishers = _read_json(PRIVATE_DIR / "publisher_research" / "publisher_results.json", [])
    validation = _read_json(PRIVATE_DIR / "email_extraction" / "validation_report.json", {})
    contacts = _read_csv(PRIVATE_DIR / "email_extraction" / "contact_intelligence.csv")
    drafts = _read_csv(PRIVATE_DIR / "email_extraction" / "outreach_drafts.csv")
    personalized = _read_csv(PRIVATE_DIR / "email_extraction" / "personalized_outreach.csv")
    replies = _read_csv(PRIVATE_DIR / "email_extraction" / "classified_replies.csv")
    negotiations = _read_csv(PRIVATE_DIR / "email_extraction" / "negotiation_results.csv")
    prospects = _read_csv(PRIVATE_DIR / "client_prospecting" / "client_prospects.csv")
    clusters = _read_csv(PRIVATE_DIR / "seo" / "keyword_clustering" / "keyword_clusters.csv")
    gaps = _read_csv(PRIVATE_DIR / "seo" / "content_gap" / "content_gap_report.csv")
    competitors = _read_csv(PRIVATE_DIR / "seo" / "competitors" / "competitor_analysis.csv")
    backlinks = _read_csv(PRIVATE_DIR / "linkbuilding" / "backlink_monitor_results.csv")
    orders = _read_csv(PRIVATE_DIR / "client_orders" / "orders.csv")
    heartbeat = _read_json(PRIVATE_DIR / "system" / "heartbeat.json", {})

    cluster_ids = {r.get("cluster_id") for r in clusters if r.get("cluster_id")}
    crm_count = _count_sqlite_rows(PRIVATE_DIR / "publisher_crm" / "publishers.db", "publishers")
    tasks_count = _count_sqlite_rows(PRIVATE_DIR / "database" / "linkbuild_ai_os.db", "central_tasks")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system": {
            "name": "LINKBUILD AI OS Brains",
            "version": "2.6 Cloud 24/7",
            "central_brain_available_scripts": brain_summary["available_agents"],
            "central_brain_total_scripts": brain_summary["total_agents"],
            "central_brain_missing_scripts": brain_summary["missing_agents"],
            "registered_brains": len(agents_registry),
            "connected_brains": sum(1 for a in agents_registry.values() if a.get("status") == "connected"),
            "heartbeat": heartbeat,
            "tasks_logged": tasks_count,
        },
        "metrics": {
            "seo_total": len(seo_status_rows),
            "seo_completed": seo_completed,
            "seo_failed": seo_failed,
            "verified_emails": validation.get("summary", {}).get("mx_found", len(contacts)),
            "total_emails": validation.get("summary", {}).get("total", len(contacts)),
            "keyword_clusters": len(cluster_ids),
            "content_gaps": sum(1 for g in gaps if g.get("status") == "CONTENT_GAP"),
            "publishers_researched": len(publishers),
            "crm_publishers": crm_count,
            "outreach_drafts": len(drafts),
            "personalized_drafts": len(personalized),
            "classified_replies": len(replies),
            "negotiations": len(negotiations),
            "client_prospects": len(prospects),
            "orders": len(orders),
            "backlinks_checked": len(backlinks),
            "competitors": len(competitors),
        },
        "seo_modules": [
            {
                "module": row.get("module", ""),
                "website": row.get("website", ""),
                "status": row.get("status", ""),
            }
            for row in seo_status_rows
        ],
        "latest_seo_run_time": latest_seo_run.get("run_time", ""),
        "publishers": [
            {
                "url": p.get("url", ""),
                "title": p.get("title", ""),
                "relevance_score": p.get("relevance_score", 0),
                "status": p.get("status", ""),
                "contact_pages": (p.get("contact_pages") or [])[:2],
            }
            for p in publishers
        ],
        "outreach_highlights": [
            {
                "email": d.get("email", ""),
                "website": d.get("website", ""),
                "contact_type": d.get("contact_type", ""),
                "priority": d.get("priority", ""),
                "subject": d.get("subject", ""),
                "approval_status": d.get("approval_status", "Pending Review"),
            }
            for d in drafts[:6]
        ],
        "brains": [
            {
                "id": key,
                "name": val.get("name", key),
                "department": val.get("department", ""),
                "status": val.get("status", ""),
            }
            for key, val in agents_registry.items()
        ],
    }

    OUTPUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Dashboard data synced to: {OUTPUT_FILE}")
    return payload


if __name__ == "__main__":
    build_dashboard_data()
