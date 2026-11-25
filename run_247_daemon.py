import csv
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.agent_runtime.dispatcher import execute_agent
from core.brain import CentralBrain
from core.dashboard_sync import build_dashboard_data
from core.database import initialize_database as init_core_db
from core.integrations.ai_integration import register_gemini_agent
from core.integrations.seo_integration import register_seo_agent
from core.orchestrator import Orchestrator
from core.task_manager.manager import (
    claim_next_task,
    recover_stale_tasks,
    update_task_status,
)

SYSTEM_DIR = PROJECT_ROOT / "data" / "private" / "system"
SYSTEM_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT_FILE = SYSTEM_DIR / "heartbeat.json"

RUNNING = True


def handle_shutdown(signum, frame):
    global RUNNING
    print("\n[24/7 DAEMON] Graceful shutdown signal received. Stopping worker loop...")
    RUNNING = False


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


def record_heartbeat(status="HEALTHY", stats=None):
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "pid": os.getpid(),
        "stats": stats or {},
    }
    with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def sync_publishers_to_crm():
    """Sync inspected publishers and verified contacts into Publisher CRM SQLite DB."""
    from agents.publisher.crm.publisher_crm import add_publisher, initialize_database

    initialize_database()
    pub_json = PROJECT_ROOT / "data" / "private" / "publisher_research" / "publisher_results.json"
    contact_csv = PROJECT_ROOT / "data" / "private" / "email_extraction" / "contact_intelligence.csv"

    email_by_host = {}
    if contact_csv.exists():
        with open(contact_csv, "r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                host = (row.get("website_name") or "").strip().lower()
                if host and host not in email_by_host and row.get("mx_found") == "True":
                    email_by_host[host] = (row.get("email", ""), row.get("contact_type", ""))

    synced = 0
    if pub_json.exists():
        try:
            records = json.loads(pub_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            records = []
        for rec in records:
            url = (rec.get("url") or "").strip()
            if not url:
                continue
            host = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
            email, ctype = email_by_host.get(host, ("", ""))
            add_publisher(
                website=url,
                email=email,
                niche="home_improvement",
                contact_type=ctype,
                notes=f"Relevance: {rec.get('relevance_score', 0)}",
            )
            synced += 1
    return synced


def run_operations_sweep():
    """Run all auxiliary operational intelligence agents cleanly."""
    from agents.clients.orders.order_manager import import_orders
    from agents.content.content_intelligence import run_analysis as run_content_intel
    from agents.email.personalizer.personalizer import main as run_personalizer
    from agents.email.reply_detector.reply_detector import main as run_reply_detector
    from agents.linkbuilding.monitor.backlink_monitor import run_monitor
    from agents.linkbuilding.placement_tracker import run_tracker
    from agents.niches.niche_intelligence import NicheIntelligence
    from agents.publisher.discovery.website_discovery import main as run_discovery
    from agents.publisher.quality.website_quality import analyze_websites
    from agents.seo.pipeline.scheduled_runner import main as run_scheduled_seo

    init_core_db()
    CentralBrain().show_status()
    run_scheduled_seo()
    run_discovery()
    analyze_websites()
    sync_publishers_to_crm()
    run_personalizer()
    run_reply_detector()
    run_tracker()
    run_monitor(check_live=True)
    import_orders()
    run_content_intel()
    NicheIntelligence()
    build_dashboard_data()


def run_daemon_cycle(orchestrator, cycle_count, run_sweep=False):
    recovered = recover_stale_tasks(max_age_minutes=15)
    if recovered:
        print(f"[24/7 DAEMON] Recovered {recovered} interrupted tasks.")

    cb_result = orchestrator.process_pending_tasks(limit=10)

    mb_processed = 0
    while True:
        task = claim_next_task()
        if not task:
            break
        task_id = task["task_id"]
        agent_id = task["agent_id"]
        command = task["command"]
        print(f"[24/7 DAEMON] Executing Master Brain Task: {task_id} -> Agent: {agent_id}")

        try:
            res = execute_agent(agent_id, command)
            status = res.get("status", "completed")
            if status not in {"completed", "needs_input", "failed"}:
                status = "completed"
            update_task_status(task_id, status, result=res)
            mb_processed += 1
        except Exception as err:
            update_task_status(task_id, "failed", error=str(err))

    if run_sweep:
        run_operations_sweep()

    stats = {
        "cycle": cycle_count,
        "central_brain_processed": cb_result.get("processed", 0),
        "master_brain_processed": mb_processed,
        "recovered_tasks": recovered,
        "sweep_executed": run_sweep,
    }
    record_heartbeat("HEALTHY", stats)
    return stats


def main(interval_seconds=30, max_cycles=None, sweep=False, sweep_every=20):
    print("=" * 60)
    print("LINKBUILD AI OS - 24/7 AUTONOMOUS DAEMON ENGINE")
    print("=" * 60)
    print(f"Process PID: {os.getpid()}")
    print(f"Cycle Interval: {interval_seconds}s")
    print(f"Heartbeat Target: {HEARTBEAT_FILE}")
    print("Autonomous agents active: SEO, Gemini/AI, Publisher, Email, Client")
    print("Press Ctrl+C to stop gracefully.")
    print("-" * 60)

    orchestrator = Orchestrator()
    register_seo_agent(orchestrator)
    register_gemini_agent(orchestrator)

    cycle = 1
    record_heartbeat("STARTING", {"cycle": 0})

    while RUNNING:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{now_str}] --- Heartbeat Cycle #{cycle} ---")

        do_sweep = (sweep and cycle == 1) or (sweep_every > 0 and cycle % sweep_every == 0)
        try:
            stats = run_daemon_cycle(orchestrator, cycle, run_sweep=do_sweep)
            print(
                f"Cycle #{cycle} finished. Tasks processed: "
                f"CB={stats['central_brain_processed']}, MB={stats['master_brain_processed']}"
            )
        except Exception as error:
            print(f"[24/7 DAEMON] Error during cycle #{cycle}: {error}")
            record_heartbeat("DEGRADED", {"error": str(error), "cycle": cycle})

        if max_cycles and cycle >= max_cycles:
            print(f"[24/7 DAEMON] Completed configured max cycles ({max_cycles}).")
            break

        for _ in range(interval_seconds):
            if not RUNNING:
                break
            time.sleep(1)

        cycle += 1

    record_heartbeat("HEALTHY", {"last_completed_cycle": cycle})
    build_dashboard_data()
    print("\n[24/7 DAEMON] Engine cleanly stopped.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LINKBUILD AI OS 24/7 Autonomous Daemon")
    parser.add_argument("--interval", type=int, default=30, help="Sleep interval in seconds between cycles")
    parser.add_argument("--cycles", type=int, default=None, help="Stop after N cycles")
    parser.add_argument("--sweep", action="store_true", help="Run full operations sweep on cycle 1")
    parser.add_argument("--sweep-every", type=int, default=20, help="Run full operations sweep every N cycles")
    args = parser.parse_args()

    main(
        interval_seconds=args.interval,
        max_cycles=args.cycles,
        sweep=args.sweep,
        sweep_every=args.sweep_every,
    )
