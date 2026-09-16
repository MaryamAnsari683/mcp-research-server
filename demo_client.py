"""End-to-end stdio MCP client demo for the Research Notes MCP Server."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent
SERVER_PATH = ROOT / "mcp_server" / "server.py"


def text_result(result) -> str:
    """Extract the first text content block from an MCP tool result."""
    for item in result.content:
        text = getattr(item, "text", None)
        if text is not None:
            return text
    raise RuntimeError("MCP server returned no text content.")


async def run_demo() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_response = await session.list_tools()
            print("\nAvailable MCP tools:")
            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\nCalling save_note...")
            saved = await session.call_tool(
                "save_note",
                arguments={
                    "title": "MCP Architecture Notes",
                    "content": "MCP lets an AI client call a server capability through a typed tool interface.",
                    "tags": "mcp,architecture,research",
                },
            )
            saved_data = json.loads(text_result(saved))
            print(json.dumps(saved_data, indent=2, ensure_ascii=False))

            print("\nCalling search_notes...")
            found = await session.call_tool(
                "search_notes",
                arguments={"query": "MCP", "limit": 5},
            )
            print(json.dumps(json.loads(text_result(found)), indent=2, ensure_ascii=False))

            print("\nCalling get_saved_note...")
            loaded = await session.call_tool(
                "get_saved_note",
                arguments={"note_id": saved_data["id"]},
            )
            print(json.dumps(json.loads(text_result(loaded)), indent=2, ensure_ascii=False))

            print("\nEnd-to-end MCP demo completed successfully.")


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
