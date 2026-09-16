from pathlib import Path

import pytest

import mcp_server.store as store


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "notes.db")
    store.initialize_store()
    return store


def test_create_and_read_note(isolated_db):
    note = isolated_db.create_note(
        title="Agent notes",
        content="MCP tools have typed inputs.",
        tags="mcp,agents",
    )

    assert note["id"] == 1
    loaded = isolated_db.get_note(1)
    assert loaded["title"] == "Agent notes"
    assert "typed inputs" in loaded["content"]


def test_search_finds_note(isolated_db):
    isolated_db.create_note(
        title="Research workflow",
        content="The client calls a local MCP server.",
        tags="demo",
    )

    results = isolated_db.search_notes(query="MCP", limit=5)
    assert len(results) == 1
    assert results[0]["title"] == "Research workflow"


def test_rejects_bad_input(isolated_db):
    with pytest.raises(ValueError, match="title cannot be empty"):
        isolated_db.create_note(title="", content="valid")

    with pytest.raises(ValueError, match="limit must be between"):
        isolated_db.search_notes(query="MCP", limit=99)

    with pytest.raises(ValueError, match="note_id must be greater"):
        isolated_db.get_note(0)


def test_rejects_unsafe_tags(isolated_db):
    with pytest.raises(ValueError, match="tags may contain only"):
        isolated_db.create_note(
            title="Valid title",
            content="Valid content",
            tags="../../secret",
        )
