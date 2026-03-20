import sqlite3
from typing import Any, Dict, List, Optional


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            job_shortcode TEXT NOT NULL,
            resume_url TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    conn.commit()


def insert_application(
    conn: sqlite3.Connection,
    name: str,
    email: str,
    job_shortcode: str,
    resume_url: str,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO applications (name, email, job_shortcode, resume_url)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, job_shortcode, resume_url),
    )
    conn.commit()
    return int(cur.lastrowid)


def list_applications(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, name, email, job_shortcode, resume_url, created_at
        FROM applications
        ORDER BY id DESC
        """
    ).fetchall()
    return [dict(r) for r in rows]

