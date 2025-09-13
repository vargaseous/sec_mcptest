# FastMCP: Build MCP Servers the Friendly Way

Curious about building your own Model Context Protocol (MCP) server in Python? FastMCP is a lightweight library that lets you expose Python functions as MCP tools with minimal code. This guide focuses on general FastMCP usage and points to this repo’s `mcp_server_fastmcp.py` as a reference where helpful.

## What Is FastMCP?

- Simple server framework for MCP over stdio.
- You write normal Python functions, decorate them with `@app.tool()`, and FastMCP turns them into callable MCP tools.
- Type hints become your parameter schema; docstrings become descriptions.
- `app.run()` handles the MCP handshake, tool listing, and routing calls to your functions.

Think of it as “write functions, get tools” — without wrestling with JSON-RPC details.

## Minimal Template (Project-Style)

A minimal FastMCP server following this project’s style: async tools that call a local REST API.

```python
from typing import Any, Dict, List
from pathlib import Path
import httpx
from fastmcp import FastMCP

API_BASE_URL = "http://localhost:8000"
app = FastMCP("streamlit-controller")

async def _api_request(method: str, endpoint: str, data: Any | None = None) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=5) as client:
        url = f"{API_BASE_URL}{endpoint}"
        resp = await client.request(method, url, json=data)
        resp.raise_for_status()
        return resp.json()

@app.tool()
async def list_facility_classes() -> List[str]:
    """List available facility class names (fclasses)."""
    data = await _api_request("GET", "/fclasses")
    return list(data.get("fclasses", []))

if __name__ == "__main__":
    app.run()
```

## Core Concepts

- Server name
  - A short identifier you choose when creating `FastMCP(...)`. Example in this repo: `mcp_server_fastmcp.py:23` uses `"streamlit-controller"`.

- Tools via decorators
  - Any function (sync or async) with `@app.tool()` becomes a tool. See examples at `mcp_server_fastmcp.py:41, 47, 54, 73, 81, 88`.

- Type hints + docstrings
  - Define input schema and human-readable descriptions automatically. Keep them clear for better client UX.

- Runtime over stdio
  - `app.run()` (see `mcp_server_fastmcp.py:115`) starts a stdio-based server. Your MCP client spawns the process and talks MCP/JSON‑RPC.

## Async I/O Pattern (As Used Here)

Most real tools call out to something: HTTP APIs, databases, local processes. Using `async` keeps the server responsive.

This project uses a shared helper that builds the URL from `API_BASE_URL` and an endpoint, then calls with `httpx.AsyncClient`:

```python
import httpx
from typing import Any, Dict

API_BASE_URL = "http://localhost:8000"

async def _api_request(method: str, endpoint: str, data: Any | None = None) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=5) as client:
        url = f"{API_BASE_URL}{endpoint}"
        resp = await client.request(method, url, json=data)
        resp.raise_for_status()
        return resp.json()
```

## Adding Your Own Tools

1) Write a function with clear type hints and a docstring.
2) Decorate it with `@app.tool()`.
3) Return JSON‑serializable values (dict, list, str, int, float, bool, None).

*Examples from this project:*

List values from the API

```python
from typing import List

@app.tool()
async def list_facility_classes() -> List[str]:
    """List available facility class names (fclasses)."""
    data = await _api_request("GET", "/fclasses")
    return list(data.get("fclasses", []))
```

Validate inputs before POSTing

```python
from typing import Dict, List, Any

@app.tool()
async def set_facility_filters(fclasses: List[str]) -> Dict[str, Any]:
    """Set visible facility classes; rejects unknown values."""
    known = await _api_request("GET", "/fclasses")
    allowed = set(known.get("fclasses", []))
    invalid = [x for x in fclasses if x not in allowed]
    if invalid:
        return {
            "status": "error",
            "message": "Some fclasses are not recognized",
            "invalid": invalid,
            "allowed": sorted(list(allowed)),
        }
    result = await _api_request("POST", "/filters", fclasses)
    return {"status": "success", **result}
```

Post structured payloads

```python
from typing import Dict, Any

@app.tool()
async def set_map_view(latitude: float, longitude: float, zoom: int) -> Dict[str, Any]:
    """Set map center (lat/lon) and zoom level."""
    payload = {"center": [latitude, longitude], "zoom": zoom}
    result = await _api_request("POST", "/map", payload)
    return {"status": "success", **result}
```

## Error Handling That Feels Nice

Clients surface exceptions to users. It’s often nicer to catch errors and return a structured result. Here’s a variant of this project’s reset tool with friendlier errors:

```python
import httpx
from typing import Any, Dict

@app.tool()
async def safe_reset() -> Dict[str, Any]:
    """Reset the app; return a clear error instead of raising."""
    try:
        result = await _api_request("DELETE", "/state")
        return {"status": "success", **result}
    except httpx.RequestError as e:
        return {"status": "error", "message": f"Network issue: {e}"}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"API returned {e.response.status_code}"}
```

## Wiring It Up to a Client

MCP clients launch your script and talk over stdio. They typically need:
- `command`: path to your Python
- `args`: script path (and any flags)
- `cwd`: working directory

Example (Claude Desktop style, matching this project):

```json
{
  "mcpServers": {
    "streamlit-controller": {
      "command": "/absolute/path/to/project/.venv/bin/python",
      "args": ["/absolute/path/to/project/mcp_server_fastmcp.py"],
      "cwd": "/absolute/path/to/project"
    }
  }
}
```

Tip from this repo: `mcp_server_fastmcp.py` detects the venv Python on Windows vs. macOS/Linux and can print a ready-to-paste config (see `mcp_server_fastmcp.py:108–113`). Feel free to copy that idea for portability.

## Common Patterns You’ll Reuse

- Small HTTP wrapper shared by tools (like `_api_request`).
- Input validation before calling out to services.
- Consistent return envelopes (e.g., `{status, message, ...}`) so client prompts can reason about results.
- Async all the way when doing I/O for concurrency and snappy UX.

## A Quick Checklist

- Clear server name in `FastMCP("...")`.
- Tools decorated and type‑hinted.
- JSON‑serializable returns.
- Friendly, actionable error messages.
- Client config points to the right Python, script, and `cwd`.

## See It in This Repo

- Name and app setup: `mcp_server_fastmcp.py:23`
- HTTP helper: `mcp_server_fastmcp.py:26`
- Tools: `mcp_server_fastmcp.py:41, 47, 54, 73, 81, 88`
- Run loop: `mcp_server_fastmcp.py:115`
- Portable client config: `mcp_server_fastmcp.py:108–113`

With these patterns, you can point FastMCP at any domain: local scripts, REST or GraphQL APIs, CLIs, or databases — and present clean, typed tools to your MCP client.

*Last updated: September 2025*