# Demonstration of a Streamlit app and MCP server

This setup allows external applications (mainly desktop LLM clients with MCP support, such as Claude Desktop and LM Studio) to control a Streamlit dashboard (an explorer of Singapore health facilities data from OpenStreetMap) through an MCP server.

This repository was prepared as part of a demonstration on Model Context Protocol (MCP) and agentic coding assistants (such as Claude Code and OpenAI Codex) for National Coding Week at the Singapore-ETH Centre.

## Architecture

1. **Streamlit App** (`main.py`) - The web interface
2. **FastAPI Server** (`api_server.py`) - REST API for state management
3. **Redis** - Shared state storage and pub/sub
4. **MCP Server** (`mcp_server.py`) - Tools for external clients (Claude Desktop / LM Studio)
   - Alternative implementation: `mcp_server_fastmcp.py` (uses fastmcp)

## Docs

- MCP overview: `docs/mcp_overview.md`
- FastMCP how-to: `docs/fastmcp_guide.md`

## Setup Guide (macOS/Linux)

### Installation

1. Install dependencies:
Make sure you already have Python and uv installed. Then, use uv to download and install the project dependencies.
```bash
uv sync
```

2. Install and start Redis:
```bash
# macOS (Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server
```

### Running the System

Start each component in its own terminal (order doesn’t matter, but all three should be running before using MCP tools):

1. Start Redis (if not running as a service):
```bash
redis-server
```

2. Start FastAPI server:
```bash
uv run api-server
```

Alternative:
```bash
python api_server.py
```

3. Start Streamlit app:
```bash
uv run streamlit run main.py
```

4. (Optional) Test MCP server directly:
```bash
uv run mcp-server
```

Alternative (fastmcp implementation):
```bash
uv run mcp-server-fast
```

## Setup Guide (Windows)

#### Installation
If you are running a Windows machine, you may need additional steps to install the prerequisites. Instead of specific instructions, we will provide a list of links that provide you different ways to install the prerequisites, as well as recommendations for what to do if you are not sure.

| Prerequisite | Recommendation |
|--------------|----------------|
| [Git for Windows](https://git-scm.com/downloads/win) | Download and install using the official installer from the Git for Windows website. |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Follow the installation instructions provided on the uv documentation page. |
| [Redis](https://redis.io/) | Redis is not natively available for Windows. Use Docker to run Redis: download the [Docker image for Redis](https://hub.docker.com/_/redis), then follow the [Docker usage guide](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/) on the Redis website. |
| [Docker](https://www.docker.com/) | To run Redis, you may want to download Docker. [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) is the easiest way to use Docker on Windows. |

Optional:
- [GitHub Desktop](https://desktop.github.com/download/): This makes it easier to manage and synchronise GitHub repositories like this one to your computer.

Then, open PowerShell (Windows Terminal) in the project directory (e.g. `...\GitHub\sec_mcptest\` if you are using GitHub Desktop to clone this repository), and run:
```shell
uv sync
```

#### Running the system

1. Start Docker Engine
If you are using Docker Desktop, open the app and log into Docker.

2. Start Redis
Open the PowerShell (Windows Terminal).

If you have not yet installed Redis, do so:
```shell
docker pull redis
```

Then, start redis (complete instructions [here](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/))
```shell
docker run -d --name redis -p 6379:6379 redis:latest
```

⚠️ IMPORTANT: Leave this PowerShell (Windows Terminal) tab running. It keeps Redis alive.

3. Start API server
Before proceeding with this step, make sure you have already run `uv sync` on the project directory.

Open *new* instances of PowerShell (Windows Terminal) in the project directory (`GitHub/sec_mcptest/`). Then start the following services:

- API server:
  - `uv run api-server`
  - or `.venv\Scripts\python.exe api_server.py`
- Streamlit app:
  - `uv run streamlit run main.py`
  - or `uv run python -m streamlit run main.py`
  - or `.venv\Scripts\streamlit.exe run main.py`
- MCP server (optional for testing):
  - `uv run mcp-server`

Everything should now be running. See below for information on how to set up your client of choice.

### WSL2 Option

- Install Ubuntu via Microsoft Store and run all commands inside WSL2.
- Follow the Linux instructions (e.g., `sudo apt install redis-server`).
- Access services from Windows at `http://localhost:8501` (Streamlit) and `http://localhost:8000` (API).

## Available MCP Tools

- `get_app_state` — Get current filters and map view
- `list_facility_classes` — List valid `fclass` values from the dataset
- `set_facility_filters` — Control visible facility types
- `set_map_view` - Set map centre and zoom level
- `reset_app` — Reset to default state
- `check_health` — Verify API↔Redis connectivity

## Prerequisites for All Integrations

- Python environment set up with `uv sync` and the virtual env located at `.venv/` (created by `uv`).
- Redis, FastAPI server, and Streamlit app running locally as shown above.

---

## Integration: Claude Desktop

Claude Desktop supports configuring MCP servers via a JSON file. This project can generate a portable config that auto-detects your project path and virtual environment.

1) Generate portable config (recommended):
```bash
uv run python mcp_server.py --config
```

Copy the printed JSON into your Claude Desktop config file. Typical locations:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

2) Manual config (if you prefer editing by hand):

#### macOS/Linux
```json
{
  "mcpServers": {
    "streamlit-controller": {
      "command": "/absolute/path/to/project/.venv/bin/python",
      "args": ["/absolute/path/to/project/mcp_server.py"],
      "cwd": "/absolute/path/to/project"
    }
  }
}
```

#### Windows
```json
{
  "mcpServers": {
    "streamlit-controller": {
      "command": "/absolute/path/to/project/.venv/Scripts/python.exe",
      "args": ["/absolute/path/to/project/mcp_server.py"],
      "cwd": "/absolute/path/to/project"
    }
  }
}
```

3) Use it in Claude:
- Ensure Redis, API, and Streamlit are running.
- Open Claude Desktop and start a new chat.
- Ask Claude to use the `streamlit-controller` tools, e.g.:
  - "Use get_app_state"
- "Set the map centre to 1.3521, 103.8198 with zoom 13"

Troubleshooting (Claude):
- If tools are not listed, recheck the `command`, `args`, and `cwd` paths.
- Ensure `uv run api-server` is running and `curl http://localhost:8000/health` returns healthy.
- If Redis isn’t running, the API health will show `"redis":"disconnected"`.

---

## Integration: LM Studio (tested on 0.3.25)

Follow these steps to register the MCP server:

1) Open the MCP configuration editor:
- Click the wrench icon (top-right) → Program.
- Click Install (to enable the MCP integration if prompted).
- Click Edit mcp.json.

2) Add the server to `mcp.json`.

#### macOS/Linux
```json
{
  "mcpServers": {
    "streamlit-controller": {
      "command": "/absolute/path/to/project/.venv/bin/python",
      "args": ["/absolute/path/to/project/mcp_server.py"],
      "cwd": "/absolute/path/to/project"
    }
  }
}
```

#### Windows
```json
{
  "mcpServers": {
    "streamlit-controller": {
      "command": "/absolute/path/to/project/.venv/Scripts/python.exe",
      "args": ["/absolute/path/to/project/mcp_server.py"],
      "cwd": "/absolute/path/to/project"
    }
  }
}
```

3) Save the file, then in LM Studio start a chat and invoke tools after ensuring Redis, API, and Streamlit are running.

Troubleshooting (LM Studio 0.3.25):
- If tools don’t show up, re-open the Program panel and ensure MCP is installed/enabled.
- Verify paths in `mcp.json` are absolute and the `.venv` has dependencies (`uv sync`).
- Check the API health at `http://localhost:8000/health` and confirm Redis is connected.

Examples of models tested and reported to work:
- `google/gemma-3-12b`
- `mistralai/devstral-small-2507`
- `openai/gpt-oss-20b`
- `qwen/qwen3-1.7b`
- `qwen/qwen3-4b-2507`
- `qwen/qwen3-4b-thinking-2507`


We have tested these on the following devices:
- 🍎 MacBook Pro 14-inch (2023), M2 Pro (10-core), 16 GB RAM
- 🪟 ThinkPad P14s (Gen 5), Intel Core Ultra 7 155H + NVIDIA RTX 500 Ada, 32 GB RAM

Both machines performed similarly, and we found:
- Qwen3-4B-2507 balanced performance and instruction-following.
- However, even Qwen3-1.7B sufficed for most use cases, and runs comfortably alongside other apps.

---

## Usage Examples

Once connected from any MCP client:
- "Show only hospitals on the map"
- "Zoom in on the central area"
- "Reset the app to show all facilities"
- "Centre the map on coordinates 1.3521, 103.8198"

## Troubleshooting (General)

- API not healthy:
  - Verify Redis is running: `redis-cli ping` → `PONG`
  - Check API logs where you ran `uv run api-server`
- Port conflicts:
  - API uses `:8000`. Change in `api_server.py` if needed and update clients accordingly.
- Wrong Python/paths:
  - Use absolute paths to `.venv/bin/python`, `mcp_server.py`, and project root.
- Dependencies:
  - Reinstall if needed: `uv sync`

## Credits

This repository was created with extensive input from Claude Code and OpenAI Codex.

Data/Maps Copyright 2018 Geofabrik GmbH and OpenStreetMap Contributors

*Last updated: September 2025*