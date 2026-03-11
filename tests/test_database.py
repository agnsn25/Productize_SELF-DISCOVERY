"""Tests for the SQLite database layer."""

import json
from unittest.mock import patch

import pytest
import pytest_asyncio

from backend.app.database import init_db, save_structure, get_structure, list_structures


# ── Fixtures ─────────────────────────────────────────────────

@pytest_asyncio.fixture(autouse=True)
async def use_memory_db():
    """Patch DB_PATH to use an in-memory SQLite database for every test."""
    with patch("backend.app.database.DB_PATH", ":memory:"):
        # In-memory DB is per-connection, so we need a different approach.
        # Instead, use a temp file.
        pass

    # In-memory DBs don't persist across connections in aiosqlite.
    # Use a temp file instead.
    import tempfile
    import os

    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_path = tmp.name
    tmp.close()

    with patch("backend.app.database.DB_PATH", tmp_path):
        await init_db()
        yield tmp_path

    os.unlink(tmp_path)


def _sample_structure_data(task: str = "solve math") -> dict:
    """Return a minimal structure dict matching what run_discovery produces."""
    return {
        "task_description": task,
        "selected_modules": ["Module A", "Module B"],
        "adapted_modules": ["Adapted A", "Adapted B"],
        "reasoning_structure": {
            "step_1": {"instruction": "do X", "reasoning_module": "Adapted A"}
        },
        "thinking_traces": {
            "select": "thought 1",
            "adapt": "thought 2",
            "implement": "thought 3",
        },
    }


# ── Tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_init_db_creates_table(use_memory_db):
    """init_db should create the structures table without error."""
    import aiosqlite

    async with aiosqlite.connect(use_memory_db) as db:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='structures'"
        )
        row = await cursor.fetchone()

    assert row is not None
    assert row[0] == "structures"


@pytest.mark.asyncio
async def test_save_and_get_structure_roundtrip(use_memory_db):
    """Saving a structure and retrieving it should return matching data."""
    data = _sample_structure_data()
    structure_id = await save_structure(data)

    assert isinstance(structure_id, str)
    assert len(structure_id) == 36  # UUID format

    retrieved = await get_structure(structure_id)

    assert retrieved is not None
    assert retrieved["id"] == structure_id
    assert retrieved["task_description"] == "solve math"
    assert retrieved["selected_modules"] == ["Module A", "Module B"]
    assert retrieved["adapted_modules"] == ["Adapted A", "Adapted B"]
    assert retrieved["reasoning_structure"]["step_1"]["instruction"] == "do X"
    assert retrieved["thinking_traces"]["select"] == "thought 1"
    assert "created_at" in retrieved


@pytest.mark.asyncio
async def test_list_structures_returns_all(use_memory_db):
    """list_structures should return all saved structures, newest first."""
    await save_structure(_sample_structure_data("task A"))
    await save_structure(_sample_structure_data("task B"))
    await save_structure(_sample_structure_data("task C"))

    results = await list_structures()

    assert len(results) == 3
    descriptions = [r["task_description"] for r in results]
    assert "task A" in descriptions
    assert "task B" in descriptions
    assert "task C" in descriptions

    # Newest first (last inserted should be first in results)
    assert results[0]["task_description"] == "task C"


@pytest.mark.asyncio
async def test_get_structure_returns_none_for_nonexistent(use_memory_db):
    """get_structure should return None when the ID doesn't exist."""
    result = await get_structure("00000000-0000-0000-0000-000000000000")
    assert result is None


@pytest.mark.asyncio
async def test_save_structure_generates_unique_ids(use_memory_db):
    """Each saved structure should get a unique UUID."""
    id1 = await save_structure(_sample_structure_data("task 1"))
    id2 = await save_structure(_sample_structure_data("task 2"))

    assert id1 != id2


@pytest.mark.asyncio
async def test_structure_json_fields_are_deserialized(use_memory_db):
    """JSON fields (selected_modules, adapted_modules, etc.) should come back as Python objects, not strings."""
    data = _sample_structure_data()
    structure_id = await save_structure(data)
    retrieved = await get_structure(structure_id)

    assert isinstance(retrieved["selected_modules"], list)
    assert isinstance(retrieved["adapted_modules"], list)
    assert isinstance(retrieved["reasoning_structure"], dict)
    assert isinstance(retrieved["thinking_traces"], dict)
