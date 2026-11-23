
from pathlib import Path
from datetime import datetime, timedelta
import json


PROJECT_ROOT = Path(__file__).resolve().parents[3]

SCHEDULE_DIR = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "pipeline"
)

SCHEDULE_FILE = SCHEDULE_DIR / "schedule_config.json"


DEFAULT_SCHEDULE = {
    "enabled": False,
    "frequency": "daily",
    "interval_hours": 24,
    "run_at": "02:00",
    "last_run": None,
    "next_run": None,
}


def load_schedule():
    if not SCHEDULE_FILE.exists():
        return DEFAULT_SCHEDULE.copy()

    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        schedule = DEFAULT_SCHEDULE.copy()
        schedule.update(data)
        return schedule

    except (json.JSONDecodeError, OSError):
        return DEFAULT_SCHEDULE.copy()


def save_schedule(schedule):
    SCHEDULE_DIR.mkdir(parents=True, exist_ok=True)

    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedule, file, indent=4)


def configure_schedule(
    frequency="daily",
    run_at="02:00",
    interval_hours=24
):
    if frequency not in ("daily", "weekly", "interval"):
        raise ValueError("Frequency must be daily, weekly, or interval")

    try:
        hour, minute = map(int, run_at.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except (ValueError, AttributeError):
        raise ValueError("run_at must use HH:MM format")

    if frequency == "interval" and interval_hours < 1:
        raise ValueError("Interval must be at least one hour")

    schedule = {
        "enabled": True,
        "frequency": frequency,
        "interval_hours": interval_hours,
        "run_at": run_at,
        "last_run": None,
        "next_run": calculate_next_run(
            frequency,
            run_at,
            interval_hours
        ),
    }

    save_schedule(schedule)
    return schedule


def calculate_next_run(
    frequency,
    run_at="02:00",
    interval_hours=24
):
    now = datetime.now()

    if frequency == "interval":
        return (
            now + timedelta(hours=interval_hours)
        ).isoformat(timespec="seconds")

    hour, minute = map(int, run_at.split(":"))

    next_run = now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    if next_run <= now:
        days = 1 if frequency == "daily" else 7
        next_run += timedelta(days=days)

    return next_run.isoformat(timespec="seconds")


def mark_run_completed():
    schedule = load_schedule()

    if not schedule["enabled"]:
        return schedule

    schedule["last_run"] = datetime.now().isoformat(
        timespec="seconds"
    )

    schedule["next_run"] = calculate_next_run(
        schedule["frequency"],
        schedule["run_at"],
        schedule["interval_hours"]
    )

    save_schedule(schedule)
    return schedule


def disable_schedule():
    schedule = load_schedule()
    schedule["enabled"] = False
    save_schedule(schedule)
    return schedule


if __name__ == "__main__":
    schedule = configure_schedule(
        frequency="daily",
        run_at="02:00"
    )

    print("SEO Pipeline schedule configured.")
    print(json.dumps(schedule, indent=4))
    print(f"Configuration file: {SCHEDULE_FILE}")
    print("Background execution is not enabled yet.")
