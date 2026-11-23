
from pathlib import Path
from datetime import datetime
import json
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[3]

LOG_DIR = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "pipeline"
    / "logs"
)

LOG_FILE = LOG_DIR / "execution_history.jsonl"


def start_run():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    run_id = str(uuid.uuid4())

    record = {
        "run_id": run_id,
        "event": "PIPELINE_STARTED",
        "status": "RUNNING",
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }

    write_log(record)
    return run_id


def log_event(run_id, event, details=None):
    record = {
        "run_id": run_id,
        "event": event,
        "details": details or {},
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    write_log(record)


def finish_run(run_id, status, summary=None):
    record = {
        "run_id": run_id,
        "event": "PIPELINE_FINISHED",
        "status": status,
        "summary": summary or {},
        "finished_at": datetime.now().isoformat(timespec="seconds"),
    }

    write_log(record)


def write_log(record):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_run_history(limit=20):
    if not LOG_FILE.exists():
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    return records[-limit:]


if __name__ == "__main__":
    run_id = start_run()

    log_event(
        run_id,
        "LOGGER_CHECK",
        {"message": "Execution logger initialized"}
    )

    finish_run(
        run_id,
        "COMPLETED",
        {"message": "Logger setup completed"}
    )

    print("Execution logger initialized.")
    print(f"Log file: {LOG_FILE}")
