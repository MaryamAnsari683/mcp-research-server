# Research Notes MCP Server

A small, safe Model Context Protocol (MCP) server that exposes a real local data capability: a persistent SQLite research-notes store. An MCP client can create, search, and retrieve notes through typed tools.

## Why this project fits the MCP task

The server demonstrates:

- **Multiple typed MCP tools:** `save_note`, `search_notes`, and `get_saved_note`.
- **Real side effects:** `save_note` writes persistent records to `data/notes.db`.
- **Input validation:** empty text, oversized values, invalid limits, invalid IDs, and unsafe tags are rejected before database writes/queries.
- **Clear server boundary:** the server only operates on its own SQLite database. It does **not** expose arbitrary filesystem access, arbitrary SQL execution, shell commands, network requests, credentials, or calendar actions.
- **End-to-end client:** `demo_client.py` connects over MCP stdio, lists the tools, and calls them through the MCP protocol.

## Architecture

```text
MCP client (demo_client.py)
        |
        | stdio / MCP
        v
Research Notes MCP Server
        |
        +--> save_note(title, content, tags)
        |
        +--> search_notes(query, limit)
        |
        +--> get_saved_note(note_id)
        |
        v
   data/notes.db
      SQLite
```

## Requirements

- Python 3.11+
- `mcp[cli]` 2.2.0
- Windows, macOS, or Linux

No external API keys are required.

## Setup (Windows)

Open CMD in the project folder:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run the end-to-end client demo

This is the easiest demo for a screen recording:

```bat
python demo_client.py
```

The client will:

1. connect to the MCP server over stdio;
2. list the available MCP tools;
3. call `save_note` (writes to SQLite);
4. call `search_notes`;
5. call `get_saved_note`;
6. print the results.

The first run creates `data/notes.db` automatically.

## Run with MCP Inspector

From the project root:

```bat
mcp dev mcp_server\server.py
```

The Inspector can discover the same tools and call them interactively.

## Tests

Run:

```bat
pytest -q
```

The tests cover note creation/retrieval, searching, validation failures, and client result parsing.

## Tool reference

### `save_note`

Typed inputs:

- `title: str`
- `content: str`
- `tags: str = ""`

Side effect: creates a persistent SQLite row.

### `search_notes`

Typed inputs:

- `query: str`
- `limit: int = 5`

Effect: searches title/content/tags using parameterized SQL.

### `get_saved_note`

Typed input:

- `note_id: int`

Effect: reads one saved note by numeric ID.

## Safety boundary

This server intentionally refuses to become a general-purpose computer-control tool. It does not accept arbitrary paths, raw SQL, shell commands, URLs, API keys, or instructions to access unrelated files. The only writable capability is the server-owned SQLite file under `data/notes.db`.

## Suggested screen-recording demo

Record a terminal window while running:

```bat
.venv\Scripts\activate
python demo_client.py
```

For the submission, show the tool list and the successful `save_note` + `search_notes` + `get_saved_note` calls in the terminal. This satisfies the "client using your server" part of the task without needing a separate GUI.

## GitHub

Do not commit `data/notes.db`. It is ignored by Git because the database is generated locally at runtime.

Typical commands:

```bat
git init
git add .
git commit -m "Build research notes MCP server"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```
