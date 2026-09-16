"""Validated local SQLite storage used by the MCP tools."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "notes.db"

MAX_TITLE = 120
MAX_CONTENT = 10_000
MAX_TAGS = 240
MAX_QUERY = 200
MAX_LIMIT = 20

_TAG_PATTERN = re.compile(r"^[A-Za-z0-9 _,-]*$")


def initialize_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _clean_text(value: str, *, field: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string.")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field} cannot be empty.")
    if len(cleaned) > max_length:
        raise ValueError(f"{field} is too long (max {max_length} characters).")
    return cleaned


def _validate_tags(tags: str) -> str:
    if not isinstance(tags, str):
        raise ValueError("tags must be a string.")
    cleaned = tags.strip()
    if len(cleaned) > MAX_TAGS:
        raise ValueError(f"tags is too long (max {MAX_TAGS} characters).")
    if not _TAG_PATTERN.fullmatch(cleaned):
        raise ValueError("tags may contain only letters, numbers, spaces, commas, hyphens, and underscores.")
    return cleaned


def create_note(*, title: str, content: str, tags: str = "") -> dict:
    initialize_store()
    title = _clean_text(title, field="title", max_length=MAX_TITLE)
    content = _clean_text(content, field="content", max_length=MAX_CONTENT)
    tags = _validate_tags(tags)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO notes(title, content, tags) VALUES (?, ?, ?)",
            (title, content, tags),
        )
        note_id = int(cursor.lastrowid)
        row = conn.execute(
            "SELECT id, title, content, tags, created_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()

    return {
        "id": row[0],
        "title": row[1],
        "content": row[2],
        "tags": row[3],
        "created_at": row[4],
    }


def search_notes(*, query: str, limit: int = 5) -> list[dict]:
    initialize_store()
    query = _clean_text(query, field="query", max_length=MAX_QUERY)
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("limit must be an integer.")
    if not 1 <= limit <= MAX_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_LIMIT}.")

    like = f"%{query}%"
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT id, title, content, tags, created_at
            FROM notes
            WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (like, like, like, limit),
        ).fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "tags": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]


def get_note(note_id: int) -> dict:
    initialize_store()
    if not isinstance(note_id, int) or isinstance(note_id, bool):
        raise ValueError("note_id must be an integer.")
    if note_id <= 0:
        raise ValueError("note_id must be greater than 0.")

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, title, content, tags, created_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()

    if row is None:
        raise ValueError(f"No note exists with id {note_id}.")

    return {
        "id": row[0],
        "title": row[1],
        "content": row[2],
        "tags": row[3],
        "created_at": row[4],
    }
