# Windows Setup Guide

This guide walks through running the Streamlit app, FastAPI server, Redis, and configuring MCP clients on Windows.

## Prerequisites

- Install uv (PowerShell):
  - `powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Git and a terminal (PowerShell or Windows Terminal)
- Optional: Docker Desktop (recommended for Redis): https://www.docker.com/products/docker-desktop

## Create Environment and Install Dependencies

From the project folder:

```powershell
uv sync
```

This creates `.venv` and installs dependencies declared in `pyproject.toml`.

## Run Redis (Windows Options)

- Docker (recommended):
  - `docker run --name redis -p 6379:6379 -d redis:7-alpine`
- WSL2 (alternative):
  - Run everything inside WSL2 (Ubuntu) and follow the Linux instructions there.
- Native Windows alternatives:
  - Use a Redis-compatible service such as Memurai (Community Edition) and configure it to listen on `localhost:6379`.

## Start Services (PowerShell, from project root)

- API server:
  - `uv run api-server`
  - or `.venv\Scripts\python.exe api_server.py`
- Streamlit app:
  - `uv run streamlit-app`
  - or `uv run python -m streamlit run main.py`
  - or `.venv\Scripts\streamlit.exe run main.py`
- MCP server (optional for testing):
  - `uv run mcp-server`

## Verify Health

```powershell
curl http://localhost:8000/health
```

Expect:

```json
{"status":"healthy","redis":"connected"}
```

## Windows + MCP Configuration

### Claude Desktop (Windows)

- Config path: `%APPDATA%\Claude\claude_desktop_config.json`
- Use Windows paths in the config:

```json
{
  "mcpServers": {
    "streamlit-controller": {
      "command": "C:\\path\\to\\project\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\project\\mcp_server.py"],
      "cwd": "C:\\path\\to\\project"
    }
  }
}
```

Notes:
- Ensure Redis, API, and Streamlit are running before using tools.
- The config generator in `mcp_server.py` prints Unix-style paths; on Windows, prefer the manual config above.

### LM Studio (0.3.25)

Steps to register the MCP server:

1) Open the MCP configuration editor:
- Click the wrench icon (top-right) → Program.
- Click Install (to enable MCP if prompted).
- Click Edit mcp.json.

2) Add the server to `mcp.json` (Windows paths):

```json
{
  "mcpServers": {
    "streamlit-controller": {
      "command": "C:\\path\\to\\project\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\project\\mcp_server.py"],
      "cwd": "C:\\path\\to\\project"
    }
  }
}
```

3) Save the file, then start a chat in LM Studio and invoke tools. Make sure Redis, API, and Streamlit are running locally.

Troubleshooting:
- If tools don’t appear, re-open the Program panel and ensure MCP is installed/enabled.
- Verify absolute paths in `mcp.json` and that `.venv` has dependencies (`uv sync`).
- Check API health at `http://localhost:8000/health` and confirm Redis is connected.

## WSL2 Option

- Install Ubuntu via Microsoft Store and run all commands inside WSL2.
- Follow the Linux instructions (e.g., `sudo apt install redis-server`).
- Access services from Windows at `http://localhost:8501` (Streamlit) and `http://localhost:8000` (API).

## Troubleshooting

- "streamlit: command not found":
  - Use `uv run streamlit-app`, `uv run python -m streamlit run main.py`, or `.venv\Scripts\streamlit.exe run main.py`.
- API unhealthy / Redis disconnected:
  - Ensure Redis is running (Docker container up or service active).
  - Check connectivity: `Test-NetConnection -ComputerName localhost -Port 6379`.
- Port conflicts:
  - API uses `:8000`, Streamlit uses `:8501`. Close conflicting apps or change ports and update configs.
- Docker not found:
  - Install Docker Desktop, or use WSL2 Redis, or a native Redis-compatible service.

