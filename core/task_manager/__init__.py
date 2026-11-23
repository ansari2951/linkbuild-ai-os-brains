import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_DIR = PROJECT_ROOT / "data" / "private" / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "linkbuild_ai_os.db"


def initialize_task_table():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                input_data TEXT,
                status TEXT DEFAULT 'PENDING',
                result TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def create_task(task_name, agent_name, input_data=None):
    initialize_task_table()

    now = datetime.now(timezone.utc).isoformat()
    serialized_data = json.dumps(input_data or {})

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute("""
            INSERT INTO tasks (
                task_name, agent_name, input_data,
                status, created_at, updated_at
            )
            VALUES (?, ?, ?, 'PENDING', ?, ?)
        """, (task_name, agent_name, serialized_data, now, now))

        return cursor.lastrowid


def get_pending_tasks(limit=50):
    initialize_task_table()

    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT * FROM tasks
            WHERE status = 'PENDING'
            ORDER BY id ASC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


def update_task_status(task_id, status, result=None, error=None):
    allowed_statuses = {
        "PENDING",
        "RUNNING",
        "COMPLETED",
        "FAILED",
        "CANCELLED"
    }

    if status not in allowed_statuses:
        raise ValueError(f"Invalid task status: {status}")

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            UPDATE tasks
            SET status = ?,
                result = ?,
                error = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            status,
            json.dumps(result) if result is not None else None,
            error,
            now,
            task_id
        ))


def get_all_tasks(limit=100):
    initialize_task_table()

    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT * FROM tasks
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]
