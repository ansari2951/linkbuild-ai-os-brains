
from pathlib import Path
from datetime import datetime
import json
import traceback


PROJECT_ROOT = Path(__file__).resolve().parents[3]

ERROR_DIR = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "pipeline"
    / "logs"
)

ERROR_FILE = ERROR_DIR / "pipeline_errors.jsonl"


def record_error(
    error,
    module_name="unknown",
    run_id=None,
    context=None
):
    ERROR_DIR.mkdir(parents=True, exist_ok=True)

    error_record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "run_id": run_id,
        "module": module_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "traceback": traceback.format_exc(),
    }

    with open(ERROR_FILE, "a", encoding="utf-8") as file:
        file.write(
            json.dumps(error_record, ensure_ascii=False) + "\n"
        )

    print(
        f"[ERROR] {module_name}: {type(error).__name__}: {error}"
    )

    return error_record


def get_recent_errors(limit=20):
    if not ERROR_FILE.exists():
        return []

    records = []

    with open(ERROR_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return records[-limit:]


def clear_error_history():
    if ERROR_FILE.exists():
        ERROR_FILE.write_text("", encoding="utf-8")
        return True

    return False


if __name__ == "__main__":
    print("SEO Pipeline Error Handler initialized.")
    print(f"Error log location: {ERROR_FILE}")
    print(f"Existing errors: {len(get_recent_errors())}")
