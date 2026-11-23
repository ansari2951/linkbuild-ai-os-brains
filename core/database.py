import sqlite3
from pathlib import Path
from contextlib import contextmanager

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_DIR = PROJECT_ROOT / "data" / "private" / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "linkbuild_ai_os.db"


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():

    tables = [

        """
        CREATE TABLE IF NOT EXISTS publishers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE NOT NULL,
            website_url TEXT,
            niche TEXT,
            contact_email TEXT,
            domain_rating REAL,
            domain_authority REAL,
            traffic INTEGER,
            status TEXT DEFAULT 'NEW',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            email TEXT,
            website TEXT,
            niche TEXT,
            status TEXT DEFAULT 'NEW',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_name TEXT NOT NULL,
            campaign_type TEXT,
            niche TEXT,
            status TEXT DEFAULT 'DRAFT',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS outreach (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            publisher_id INTEGER,
            recipient_email TEXT,
            subject TEXT,
            message TEXT,
            status TEXT DEFAULT 'DRAFT',
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY (publisher_id) REFERENCES publishers(id)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            outreach_id INTEGER,
            reply_text TEXT,
            reply_type TEXT DEFAULT 'UNCLASSIFIED',
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (outreach_id) REFERENCES outreach(id)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS placements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publisher_id INTEGER,
            client_id INTEGER,
            target_url TEXT,
            published_url TEXT,
            anchor_text TEXT,
            placement_type TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (publisher_id) REFERENCES publishers(id),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
        """
    ]

    with get_connection() as connection:
        for table in tables:
            connection.execute(table)


if __name__ == "__main__":
    initialize_database()
    print("LINKBUILD AI OS database initialized.")