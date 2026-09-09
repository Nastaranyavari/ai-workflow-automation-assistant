import sqlite3
from pathlib import Path


DB_PATH = Path("data/assistant.db")


def save_record(
    title: str,
    content: str,
) -> dict:
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            INSERT INTO records (title, content)
            VALUES (?, ?)
            """,
            (title, content),
        )

        connection.commit()

        return {
            "success": True,
            "record_id": cursor.lastrowid,
        }

    finally:
        connection.close()


def search_records(keyword: str) -> list[dict]:
    if not DB_PATH.exists():
        return []

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, title, content
            FROM records
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY id DESC
            """,
            (f"%{keyword}%", f"%{keyword}%"),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()