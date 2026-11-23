
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PIPELINE_FILE = (
    PROJECT_ROOT
    / "agents"
    / "seo"
    / "pipeline"
    / "seo_pipeline.py"
)

SCHEDULE_FILE = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "pipeline"
    / "schedule_config.json"
)


def load_schedule():
    if not SCHEDULE_FILE.exists():
        print("No schedule configuration found.")
        return None

    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not load schedule: {error}")
        return None


def is_run_due(schedule):
    if not schedule or not schedule.get("enabled"):
        return False

    next_run = schedule.get("next_run")

    if not next_run:
        return False

    try:
        scheduled_time = datetime.fromisoformat(next_run)
        return datetime.now() >= scheduled_time
    except ValueError:
        print("Invalid next_run date in schedule configuration.")
        return False


def launch_pipeline():
    if not PIPELINE_FILE.is_file():
        print("SEO pipeline file not found.")
        return False

    print("Scheduled SEO pipeline is starting...")

    try:
        result = subprocess.run(
            [sys.executable, str(PIPELINE_FILE)],
            cwd=str(PROJECT_ROOT),
            check=False,
        )

        if result.returncode == 0:
            print("Pipeline process completed.")
            return True

        print(f"Pipeline process returned code: {result.returncode}")
        return False

    except OSError as error:
        print(f"Could not launch pipeline: {error}")
        return False


def main():
    schedule = load_schedule()

    if not schedule:
        return

    if not is_run_due(schedule):
        print("No scheduled SEO run is due right now.")
        return

    success = launch_pipeline()

    if success:
        from agents.seo.pipeline.scheduler import mark_run_completed

        updated = mark_run_completed()
        print("Schedule updated.")
        print(f"Next run: {updated.get('next_run')}")
    else:
        print("Pipeline failed. Schedule was not advanced.")


if __name__ == "__main__":
    main()
