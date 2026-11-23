from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "monitoring" / "logs"
TASK_LOG = LOG_DIR / "tasks.jsonl"

APP_NAME = "LINKBUILD AI OS"
APP_VERSION = "1.0.0"

LOG_DIR.mkdir(parents=True, exist_ok=True)
