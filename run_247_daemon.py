
import os
import sys
import time
import json
import signal
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.orchestrator import Orchestrator
from core.integrations.seo_integration import register_seo_agent
from core.integrations.ai_integration import register_gemini_agent
from core.master_brain.router import route_task
from core.task_manager.manager import (
    recover_stale_tasks,
    claim_next_task,
    update_task_status
)
from core.agent_runtime.dispatcher import execute_agent

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
        "stats": stats or {}
    }
    with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_daemon_cycle(orchestrator, cycle_count):
    # 1. Recover any stale or interrupted tasks
    recovered = recover_stale_tasks(max_age_minutes=15)
    if recovered:
        print(f"[24/7 DAEMON] Recovered {recovered} interrupted tasks.")

    # 2. Process Central Brain queue
    cb_result = orchestrator.process_pending_tasks(limit=10)
    
    # 3. Process Master Brain task queue
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
            update_task_status(task_id, status, result=res)
            mb_processed += 1
        except Exception as err:
            update_task_status(task_id, "failed", error=str(err))

    stats = {
        "cycle": cycle_count,
        "central_brain_processed": cb_result.get("processed", 0),
        "master_brain_processed": mb_processed,
        "recovered_tasks": recovered
    }
    record_heartbeat("HEALTHY", stats)
    return stats


def main(interval_seconds=30, max_cycles=None):
    print("=" * 60)
    print("LINKBUILD AI OS - 24/7 AUTONOMOUS DAEMON ENGINE")
    print("=" * 60)
    print(f"Process PID: {os.getpid()}")
    print(f"Cycle Interval: {interval_seconds}s")
    print(f"Heartbeat Target: {HEARTBEAT_FILE}")
    print("Autonomous agents active: SEO, Gemini, Publisher, Email, Client")
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
        
        try:
            stats = run_daemon_cycle(orchestrator, cycle)
            print(f"Cycle #{cycle} finished. Tasks processed: CB={stats['central_brain_processed']}, MB={stats['master_brain_processed']}")
        except Exception as error:
            print(f"[24/7 DAEMON] Error during cycle #{cycle}: {error}")
            record_heartbeat("DEGRADED", {"error": str(error), "cycle": cycle})

        if max_cycles and cycle >= max_cycles:
            print(f"[24/7 DAEMON] Completed configured max cycles ({max_cycles}).")
            break

        # Sleep interval with responsive shutdown checks
        for _ in range(interval_seconds):
            if not RUNNING:
                break
            time.sleep(1)

        cycle += 1

    record_heartbeat("STOPPED", {"final_cycle": cycle})
    print("\n[24/7 DAEMON] Engine cleanly stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LINKBUILD AI OS 24/7 Autonomous Daemon")
    parser.add_argument("--interval", type=int, default=30, help="Sleep interval in seconds between cycles (default 30s)")
    parser.add_argument("--cycles", type=int, default=None, help="Stop after N cycles (optional, default runs indefinitely)")
    args = parser.parse_args()

    main(interval_seconds=args.interval, max_cycles=args.cycles)
