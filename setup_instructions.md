# Streamlit MCP Server Setup

This setup allows external applications (like Claude Desktop) to control your Streamlit health facilities app through an MCP server.

## Architecture

1. **Streamlit App** (`main.py`) - The web interface
2. **FastAPI Server** (`api_server.py`) - REST API for state management  
3. **Redis** - Shared state storage
4. **MCP Server** (`mcp_server.py`) - Interface for Claude Desktop/LM Studio

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Install and start Redis:
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian  
sudo apt install redis-server
sudo systemctl start redis-server
```

## Running the System

Start all components in separate terminals:

1. **Start Redis** (if not running as service):
```bash
redis-server
```

2. **Start FastAPI server**:
```bash
uv run api-server
```

3. **Start Streamlit app**:
```bash
uv run streamlit-app
```

4. **Test MCP server** (optional):
```bash
uv run mcp-server
```

## Available MCP Tools

- `get_app_state` - Get current filters and map view
- `set_facility_filters` - Control which facility types are shown
- `set_map_view` - Set map center and zoom level  
- `reset_app` - Reset to default state
- `check_health` - Verify all services are running

## Integration with Claude Desktop

**Generate Portable Config (Recommended):**
```bash
uv run python mcp_server.py --config
```

This will generate a portable configuration that automatically detects your project location and virtual environment. Copy the output to your `claude_desktop_config.json` file.

**Manual Config (if needed):**
```json
{
  "mcpServers": {
    "streamlit-controller": {
      "command": "/path/to/your/project/.venv/bin/python", 
      "args": ["/path/to/your/project/mcp_server.py"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

## Usage Examples

Once connected via Claude Desktop:
- "Show only hospitals on the map"
- "Zoom in on the central area"  
- "Reset the app to show all facilities"
- "Center the map on coordinates 1.3521, 103.8198"