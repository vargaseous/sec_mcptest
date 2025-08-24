#!/usr/bin/env python3

import asyncio
import json
from pathlib import Path
from typing import Any
import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities
import mcp.server.stdio
import mcp.types as types

# Auto-detect project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"

server = Server("streamlit-controller")

API_BASE_URL = "http://localhost:8000"

async def make_api_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make HTTP request to the FastAPI server"""
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(f"{API_BASE_URL}{endpoint}")
            elif method.upper() == "POST":
                response = await client.post(f"{API_BASE_URL}{endpoint}", json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(f"{API_BASE_URL}{endpoint}")
            
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise Exception(f"API request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"API returned error {e.response.status_code}: {e.response.text}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for Streamlit manipulation"""
    return [
        types.Tool(
            name="get_app_state",
            description="Get the current state of the Streamlit app including selected filters and map view",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="set_facility_filters",
            description="Set which facility classes are visible on the map",
            inputSchema={
                "type": "object", 
                "properties": {
                    "fclasses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of facility class names to display"
                    }
                },
                "required": ["fclasses"]
            }
        ),
        types.Tool(
            name="set_map_view",
            description="Set the map center location and zoom level",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Map center latitude"
                    },
                    "longitude": {
                        "type": "number", 
                        "description": "Map center longitude"
                    },
                    "zoom": {
                        "type": "integer",
                        "description": "Map zoom level (1-20)"
                    }
                },
                "required": ["latitude", "longitude", "zoom"]
            }
        ),
        types.Tool(
            name="reset_app",
            description="Reset the app to its default state",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="check_health",
            description="Check if the API server and Redis are healthy",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle tool execution"""
    
    if name == "get_app_state":
        result = await make_api_request("GET", "/state")
        return [types.TextContent(
            type="text",
            text=f"Current app state:\n{json.dumps(result, indent=2)}"
        )]
    
    elif name == "set_facility_filters":
        fclasses = arguments.get("fclasses", [])
        result = await make_api_request("POST", "/filters", fclasses)
        return [types.TextContent(
            type="text", 
            text=f"Facility filters updated: {result['selected_fclasses']}"
        )]
    
    elif name == "set_map_view":
        lat = arguments["latitude"]
        lng = arguments["longitude"] 
        zoom = arguments["zoom"]
        
        map_data = {
            "center": [lat, lng],
            "zoom": zoom
        }
        result = await make_api_request("POST", "/map", map_data)
        return [types.TextContent(
            type="text",
            text=f"Map view updated: center [{lat}, {lng}], zoom {zoom}"
        )]
    
    elif name == "reset_app":
        result = await make_api_request("DELETE", "/state")
        return [types.TextContent(
            type="text",
            text="App state reset to defaults"
        )]
    
    elif name == "check_health":
        result = await make_api_request("GET", "/health")
        return [types.TextContent(
            type="text",
            text=f"Health check: {result['status']}, Redis: {result['redis']}"
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main entry point"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="streamlit-controller",
                server_version="0.1.0",
                capabilities=ServerCapabilities(
                    tools={},
                )
            )
        )

def generate_claude_config():
    """Generate portable Claude Desktop config"""
    config = {
        "mcpServers": {
            "streamlit-controller": {
                "command": str(VENV_PYTHON),
                "args": [str(PROJECT_ROOT / "mcp_server.py")],
                "cwd": str(PROJECT_ROOT)
            }
        }
    }
    return json.dumps(config, indent=2)

def main_sync():
    """Synchronous entry point for uv script"""
    asyncio.run(main())

def print_config():
    """Print the portable Claude Desktop config"""
    print("=== Portable Claude Desktop Config ===")
    print(generate_claude_config())
    print("\n=== Instructions ===")
    print(f"1. Copy the above config to your claude_desktop_config.json")
    print(f"2. Project detected at: {PROJECT_ROOT}")
    print(f"3. Virtual env at: {VENV_PYTHON}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        print_config()
    else:
        main_sync()