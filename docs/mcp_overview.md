# Model Context Protocol (MCP) Overview

This document explains what MCP is, why it’s useful, which popular tools support it (Claude Desktop and LM Studio), and why you might want to pair it with local, on‑device models via LM Studio.

## What Is MCP?

The Model Context Protocol (MCP) is a simple, open way for AI assistants to call out to external capabilities in a controlled and well‑described manner. Instead of hard‑coding integrations into each assistant, you run a small “server” that advertises its available actions (tools) and how to call them. The assistant connects to that server—typically over JSON‑RPC via stdio or a socket—discovers the tool list, validates parameters using the tool’s type hints, and invokes actions as needed during a conversation. Think of MCP as the glue between a model and the stuff you want it to do: APIs, databases, local scripts, or anything else you can reach from code—packaged behind clear, typed, permissioned operations.

## Why Use MCP?

- Consistency: Unified interface across different assistants and runtimes.
- Portability: The same server works in multiple clients (e.g., Claude Desktop, LM Studio).
- Safety by design: Clients only see the tools you explicitly expose; parameters are typed and validated.
- Reusability: Package project logic once as tools, reuse anywhere with MCP support.
- Separation of concerns: Keep UI, API, and MCP tools modular.

## Where You Can Use MCP Today

Two friendly places to try MCP right now are Claude Desktop and LM Studio. In Claude Desktop (macOS/Windows), you paste a small JSON snippet into its configuration that points to your MCP server script. Claude then lists your tools in the chat sidebar and can call them with typed inputs as part of normal conversation. In LM Studio, you enable the MCP integration and add your server to `mcp.json`; from there, any local model you load can discover and use your tools. Both clients make it easy to iterate: change your server, restart the chat, and you’ll see updated tools reflected immediately. Other clients may add MCP support over time, but these two are excellent starting points for hands‑on experimentation.

## How MCP Fits This Project

In this repository, we use the FastMCP library to stand up a compact MCP server that exposes a handful of tools. Those tools don’t do heavy lifting themselves—they call a local FastAPI (`api_server.py`), which in turn manages state and updates a Streamlit app (`main.py`). This keeps responsibilities clean: the MCP layer focuses on describing tools and validating inputs, the API handles business logic, and Streamlit renders the UI. The file to peek at is `mcp_server_fastmcp.py`, which defines the server name, a small async HTTP helper, and several `@app.tool()` functions. For convenience, it can also print a ready‑to‑paste Claude Desktop config and auto‑detects your virtualenv’s Python on macOS, Linux, and Windows so the client launches the right interpreter.

## Using MCP with Claude Desktop (Quick Sketch)

1) Generate a config snippet:
   - `python mcp_server_fastmcp.py --config`
2) Paste it into your Claude Desktop config (see repo `README.md` for OS‑specific paths).
3) Ensure your server’s dependencies are installed and that your API (if any) is reachable.
4) Start a chat and use your tools by name (e.g., `list_facility_classes`).

## Using MCP with LM Studio (Quick Sketch)

1) Open the Program panel and enable MCP if prompted.
2) Edit `mcp.json` and add your server (see `README.md` for an example).
3) Start a chat with a local model and call your tools.

## The Case for Local, On‑Device Models with LM Studio

We often associate large language models (LLMs) with the need to connect to an external compute facility over the internet. This is certainly the case for popular end-user platforms such as ChatGPT, Claude, and Gemini. Even users of open-weight large language models usually run these models on a server.

*Note:* Many people use the term 'open-source' to describe models such as Llama, Deepseek, and Qwen where the weights are made available for people to run on their own compute facilities or devices. These are more accurately termed 'open-weight.' To claim that their model is fully 'open-source,' developers may provide training data, pipelines, and other necessary code, as well as a technical report. Among the largest fully 'open-source' LLM efforts so far (as of 2025 September) is Apertus, developed by EPFL, ETH Zurich, and the Swiss National Supercomputing Centre (CSCS). ~~Of course, as ETH researchers, we are quite partial ;)~~ [Learn more](https://www.swiss-ai.org/apertus)

Improvements in training, distillation, and quantisation (among others), as well as the emergence of user-friendly tools like LM Studio, now make it possible to run smaller LLMs entirely on your device. Of course, the performance of these models depends on the hardware available, as well as the model's size.

Running local, on-device models has a number of key advantages:
- You can ensure the privacy of user data, as you control how data is transferred between applications.
- Your setup works without an internet connection.
- While there remains significant environmental impact from training even open-source and open-weight models, you can significantly minimise the environmental impact of *deploying* AI by using lightweight AI models on-device rather than relying on sophisticated, very large models for simple tasks such as toggling features on/off.

Running MCP tools with a local model in LM Studio can be a great experience: your prompts, tool calls, and data stay on your machine; there are no per‑token API fees; and responses arrive without cloud round‑trips. This makes local models ideal for iterative development, sensitive data, prototyping in low‑connectivity environments, or simply experimenting with different model families at your own pace. The trade‑off is that quality and speed depend on your hardware and the model you choose: smaller models are fast and private but may need more guidance, while larger ones are more capable but heavier on memory and compute. LM Studio makes it easy to try several options and pick the right balance for your workflow.

## Good Practices for MCP Servers

- Keep tool boundaries clear and focused; one action per tool is easier to compose.
- Use precise type hints and helpful docstrings—clients surface these to users.
- Validate inputs and return structured errors (`{"status":"error", "message": ...}`) when appropriate.
- Prefer async I/O for network or disk operations to stay responsive.
- Log tool calls and errors during development to simplify debugging.

## Learn More in This Repo

- FastMCP how‑to: `docs/fastmcp_guide.md`
- FastMCP server reference: `mcp_server_fastmcp.py`
- API and app: `api_server.py`, `main.py`
