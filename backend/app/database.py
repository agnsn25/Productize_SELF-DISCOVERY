import json
import uuid
from datetime import datetime, timezone

import aiosqlite

from .config import settings

DB_PATH = settings.database_path


async def init_db() -> None:
    """Create the structures table if it doesn't already exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS structures (
                id                  TEXT PRIMARY KEY,
                task_description    TEXT NOT NULL,
                selected_modules    TEXT NOT NULL,   -- JSON array
                adapted_modules     TEXT NOT NULL,   -- JSON array
                reasoning_structure TEXT NOT NULL,   -- JSON object
                thinking_traces     TEXT NOT NULL,   -- JSON object
                created_at          TEXT NOT NULL,
                discovery_usage     TEXT             -- JSON object (nullable for legacy rows)
            )
            """
        )
        try:
            await db.execute("ALTER TABLE structures ADD COLUMN discovery_usage TEXT")
        except Exception:
            pass
        await db.commit()


async def save_structure(structure_data: dict) -> str:
    """Insert a new structure row and return its generated UUID."""
    structure_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    discovery_usage = structure_data.get("discovery_usage")
    discovery_usage_json = json.dumps(discovery_usage) if discovery_usage else None

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO structures
                (id, task_description, selected_modules, adapted_modules,
                 reasoning_structure, thinking_traces, created_at, discovery_usage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                structure_id,
                structure_data["task_description"],
                json.dumps(structure_data["selected_modules"]),
                json.dumps(structure_data["adapted_modules"]),
                json.dumps(structure_data["reasoning_structure"]),
                json.dumps(structure_data["thinking_traces"]),
                created_at,
                discovery_usage_json,
            ),
        )
        await db.commit()

    return structure_id


async def get_structure(structure_id: str) -> dict | None:
    """Return a single structure dict or None if not found."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM structures WHERE id = ?", (structure_id,)
        )
        row = await cursor.fetchone()

    if row is None:
        return None

    return _row_to_dict(row)


async def list_structures() -> list[dict]:
    """Return all structures ordered by creation time (newest first)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM structures ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()

    return [_row_to_dict(r) for r in rows]


def _row_to_dict(row) -> dict:
    raw_usage = row["discovery_usage"] if "discovery_usage" in row.keys() else None
    return {
        "id": row["id"],
        "task_description": row["task_description"],
        "selected_modules": json.loads(row["selected_modules"]),
        "adapted_modules": json.loads(row["adapted_modules"]),
        "reasoning_structure": json.loads(row["reasoning_structure"]),
        "thinking_traces": json.loads(row["thinking_traces"]),
        "created_at": row["created_at"],
        "discovery_usage": json.loads(raw_usage) if raw_usage else None,
    }
