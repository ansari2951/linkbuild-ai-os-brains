
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "private" / "publisher_crm"
DB_FILE = DATA_DIR / "publishers.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS publishers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL UNIQUE,
                contact_name TEXT,
                email TEXT,
                niche TEXT,
                contact_type TEXT,
                guest_post_price REAL,
                link_insertion_price REAL,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT 'NEW',
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()


def add_publisher(
    website,
    contact_name="",
    email="",
    niche="",
    contact_type="",
    guest_post_price=None,
    link_insertion_price=None,
    currency="USD",
    notes=""
):
    website = website.strip().lower()

    if not website:
        raise ValueError("Website is required.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO publishers (
                website, contact_name, email, niche,
                contact_type, guest_post_price,
                link_insertion_price, currency,
                status, notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?, ?, ?)
            ON CONFLICT(website) DO UPDATE SET
                contact_name = excluded.contact_name,
                email = excluded.email,
                niche = excluded.niche,
                contact_type = excluded.contact_type,
                guest_post_price = excluded.guest_post_price,
                link_insertion_price = excluded.link_insertion_price,
                currency = excluded.currency,
                notes = excluded.notes,
                updated_at = excluded.updated_at
        """, (
            website, contact_name, email, niche,
            contact_type, guest_post_price,
            link_insertion_price, currency,
            notes, now, now
        ))
        conn.commit()


def update_status(website, status):
    allowed_statuses = {
        "NEW", "CONTACTED", "REPLIED",
        "NEGOTIATING", "ACCEPTED",
        "REJECTED", "ACTIVE", "INACTIVE"
    }

    status = status.strip().upper()

    if status not in allowed_statuses:
        raise ValueError("Invalid publisher status.")

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE publishers
            SET status = ?, updated_at = ?
            WHERE website = ?
        """, (
            status,
            datetime.now(timezone.utc).isoformat(),
            website.strip().lower()
        ))
        conn.commit()
        return cursor.rowcount > 0


def search_publishers(keyword=""):
    keyword = keyword.strip()

    with get_connection() as conn:
        if keyword:
            pattern = f"%{keyword}%"
            rows = conn.execute("""
                SELECT * FROM publishers
                WHERE website LIKE ?
                   OR email LIKE ?
                   OR niche LIKE ?
                   OR contact_name LIKE ?
                ORDER BY updated_at DESC
            """, (pattern, pattern, pattern, pattern)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM publishers
                ORDER BY updated_at DESC
            """).fetchall()

    return [dict(row) for row in rows]


def main():
    initialize_database()

    print("Publisher CRM database initialized.")
    print(f"Database location: {DB_FILE}")

    publishers = search_publishers()
    print(f"Total publishers saved: {len(publishers)}")


if __name__ == "__main__":
    main()
