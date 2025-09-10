#!/usr/bin/env python3

import asyncio
import json
from pathlib import Path
from typing import Any, List, Dict

import httpx

try:
    from fastmcp import FastMCP
except Exception as e:
    raise RuntimeError(
        "fastmcp is not installed. Run `uv sync` to install dependencies."
    ) from e


PROJECT_ROOT = Path(__file__).parent.absolute()
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe" if (PROJECT_ROOT / ".venv" / "Scripts" / "python.exe").exists() else PROJECT_ROOT / ".venv" / "bin" / "python"

API_BASE_URL = "http://localhost:8000"

app = FastMCP("streamlit-controller")


async def _api_request(method: str, endpoint: str, data: Any | None = None) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=5) as client:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            resp = await client.get(url)
        elif method == "POST":
            resp = await client.post(url, json=data)
        elif method == "DELETE":
            resp = await client.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")
        resp.raise_for_status()
        return resp.json()


@app.tool()
async def get_app_state() -> Dict[str, Any]:
    """Get the current state of the Streamlit app including selected filters and map view."""
    return await _api_request("GET", "/state")


@app.tool()
async def list_facility_classes() -> List[str]:
    """List all available facility class names (fclasses) from the dataset."""
    data = await _api_request("GET", "/fclasses")
    return list(data.get("fclasses", []))


@app.tool()
async def set_facility_filters(fclasses: List[str]) -> Dict[str, Any]:
    """Set which facility classes are visible on the map. Rejects unknown values."""
    # Validate against known fclasses
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


@app.tool()
async def set_map_view(latitude: float, longitude: float, zoom: int) -> Dict[str, Any]:
    """Set the map center location (lat/lon) and zoom level."""
    payload = {"center": [latitude, longitude], "zoom": zoom}
    result = await _api_request("POST", "/map", payload)
    return {"status": "success", **result}


@app.tool()
async def reset_app() -> Dict[str, Any]:
    """Reset the app to its default state."""
    result = await _api_request("DELETE", "/state")
    return {"status": "success", **result}


@app.tool()
async def check_health() -> Dict[str, Any]:
    """Check if the API server and Redis are healthy."""
    return await _api_request("GET", "/health")


def generate_claude_config() -> str:
    """Generate a portable Claude Desktop config for this server."""
    config = {
        "mcpServers": {
            "streamlit-controller": {
                "command": str(VENV_PYTHON),
                "args": [str(PROJECT_ROOT / "mcp_server_fastmcp.py")],
                "cwd": str(PROJECT_ROOT),
            }
        }
    }
    return json.dumps(config, indent=2)


def main() -> None:
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        print("=== Portable Claude Desktop Config (fastmcp) ===")
        print(generate_claude_config())
        return

    # Run the MCP server over stdio
    app.run()


if __name__ == "__main__":
    main()

