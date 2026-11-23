
import json
import sqlite3
import uuid

from datetime import datetime, timezone
from core.master_brain.config import PROJECT_ROOT


DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "database"
    / "linkbuild_ai_os.db"
)

MAX_RETRIES = 3


def current_time():
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        str(DATABASE_PATH),
        timeout=30
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")

    return connection


def initialize_task_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS central_tasks (
                task_id TEXT PRIMARY KEY,
                command TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued',
                result_json TEXT,
                error TEXT,
                retry_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(central_tasks)"
            ).fetchall()
        }

        if "retry_count" not in columns:
            connection.execute("""
                ALTER TABLE central_tasks
                ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0
            """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_central_tasks_status
            ON central_tasks(status)
        """)


def create_task(command, agent_id):
    if not isinstance(command, str) or not command.strip():
        raise ValueError("Task command cannot be empty.")

    if not isinstance(agent_id, str) or not agent_id.strip():
        raise ValueError("Agent ID cannot be empty.")

    initialize_task_database()

    timestamp = current_time()
    task_id = str(uuid.uuid4())

    task = {
        "task_id": task_id,
        "command": command.strip(),
        "agent_id": agent_id.strip(),
        "status": "queued",
        "retry_count": 0,
        "created_at": timestamp,
        "updated_at": timestamp
    }

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO central_tasks (
                task_id, command, agent_id, status,
                retry_count, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task["task_id"],
            task["command"],
            task["agent_id"],
            task["status"],
            task["retry_count"],
            task["created_at"],
            task["updated_at"]
        ))

    return task


def claim_next_task():
    initialize_task_database()

    with get_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")

        row = connection.execute("""
            SELECT *
            FROM central_tasks
            WHERE status = 'queued'
            ORDER BY created_at ASC
            LIMIT 1
        """).fetchone()

        if row is None:
            return None

        timestamp = current_time()

        cursor = connection.execute("""
            UPDATE central_tasks
            SET status = 'running',
                updated_at = ?
            WHERE task_id = ?
              AND status = 'queued'
        """, (timestamp, row["task_id"]))

        if cursor.rowcount != 1:
            return None

        task = dict(row)
        task["status"] = "running"
        task["updated_at"] = timestamp

        return task


def get_pending_tasks(limit=20):
    initialize_task_database()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM central_tasks
            WHERE status = 'queued'
            ORDER BY created_at ASC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


def update_task_status(task_id, status, result=None, error=None):
    allowed_statuses = {
        "queued",
        "running",
        "completed",
        "needs_input",
        "failed"
    }

    if status not in allowed_statuses:
        raise ValueError(f"Invalid task status: {status}")

    result_json = (
        json.dumps(result, ensure_ascii=False)
        if result is not None
        else None
    )

    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE central_tasks
            SET status = ?,
                result_json = ?,
                error = ?,
                updated_at = ?
            WHERE task_id = ?
        """, (
            status,
            result_json,
            error,
            current_time(),
            task_id
        ))

        if cursor.rowcount == 0:
            raise ValueError(f"Task not found: {task_id}")


def recover_stale_tasks(max_age_minutes=30):
    initialize_task_database()

    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE central_tasks
            SET status = CASE
                    WHEN retry_count < ? THEN 'queued'
                    ELSE 'failed'
                END,
                retry_count = retry_count + 1,
                error = 'Recovered after an interrupted execution.',
                updated_at = ?
            WHERE status = 'running'
              AND updated_at < datetime('now', ?)
        """, (
            MAX_RETRIES,
            current_time(),
            f"-{max_age_minutes} minutes"
        ))

        return cursor.rowcount


def get_task(task_id):
    initialize_task_database()

    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM central_tasks
            WHERE task_id = ?
        """, (task_id,)).fetchone()

    if row is None:
        return None

    task = dict(row)

    task["result"] = (
        json.loads(task["result_json"])
        if task["result_json"]
        else None
    )

    task.pop("result_json", None)

    return task


def get_all_tasks(limit=100):
    initialize_task_database()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM central_tasks
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


initialize_task_database()
