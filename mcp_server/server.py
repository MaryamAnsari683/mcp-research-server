"""MCP server exposing a small, safe research-notes data store.

The server deliberately limits itself to operations on one SQLite database
inside this project. It does not expose arbitrary filesystem access,
SQL execution, network requests, shell commands, or calendar operations.
"""

import json
import sqlite3
from pathlib import Path

from mcp.server import MCPServer

try:
    from mcp_server.store import (
        create_note,
        get_note,
        initialize_store,
        search_notes as search_notes_impl,
    )
except ModuleNotFoundError:  # Allows `python mcp_server/server.py` on Windows.
    from store import create_note, get_note, initialize_store, search_notes as search_notes_impl


mcp = MCPServer("Research Notes MCP Server")


@mcp.tool()
def save_note(title: str, content: str, tags: str = "") -> str:
    """Save a research note to the server's local SQLite store.

    Inputs are validated by the server. The tool only writes to the project's
    data/notes.db file; it cannot write to arbitrary user paths.
    """
    note = create_note(title=title, content=content, tags=tags)
    return json.dumps(note, ensure_ascii=False)


@mcp.tool()
def search_notes(query: str, limit: int = 5) -> str:
    """Search saved research notes by title, content, or tags."""
    notes = search_notes_impl(query=query, limit=limit)
    return json.dumps(notes, ensure_ascii=False)


@mcp.tool()
def get_saved_note(note_id: int) -> str:
    """Read one saved research note by numeric ID."""
    note = get_note(note_id)
    return json.dumps(note, ensure_ascii=False)


if __name__ == "__main__":
    initialize_store()
    mcp.run()
