# AI Coding Tools Installation Guide
## Singapore-ETH Centre Workshop

This guide provides streamlined setup instructions for three tools: Claude Code, Codex (VS Code extension and CLI), and Qwen Code. We assume that you will be using user plans (e.g. ChatGPT Plus, Claude Pro) and not API key-based flexible billing to avoid surprise costs, although this subjects you to usage limits from the services.

## Prerequisites

Use this checklist to prepare your machine. Follow the quick install steps per item.

Checklist
- [ ] Git + Bash (Windows: Git for Windows includes Git Bash)
- [ ] Node.js LTS + npm
- [ ] Python 3.10+ and `uv`
- [ ] IDE (VS Code recommended)
- [ ] LM Studio
- [ ] Claude Desktop (if you have a Claude Pro/Max plan)

Install Steps (Quickstart)
- Git + Bash
  - macOS: `brew install git` (or `xcode-select --install`)
  - Windows: Install "Git for Windows" (includes Git Bash) or `winget install Git.Git`
  - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y git`
  - Verify: `git --version` (Windows users can open "Git Bash" from Start Menu)

- Node.js LTS + npm
  - macOS/Linux (via nvm):
    - Install nvm: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash`
    - Then: `nvm install --lts`
  - Windows: `winget install OpenJS.NodeJS.LTS` (or download the LTS installer from nodejs.org)
  - Verify: `node -v` and `npm -v`

- Python 3.10+ and uv
  - macOS: `brew install python` (or use system Python 3 if up to date)
  - Windows: `winget install Python.Python.3.12`
  - Ubuntu/Debian: `sudo apt-get install -y python3 python3-venv python3-pip`
  - Install uv:
    - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    - Windows (PowerShell): `powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - Verify: `uv --version`

- IDE (VS Code)
  - Download: https://code.visualstudio.com/
  - macOS: `brew install --cask visual-studio-code`
  - Windows: `winget install Microsoft.VisualStudioCode`
  - Ubuntu (snap): `sudo snap install code --classic`

- LM Studio
  - Download: https://lmstudio.ai/
  - Install the package for your OS and follow on-screen instructions.

- Claude Desktop (optional)
  - Download: https://claude.ai/download
  - Sign in with your Anthropic account. A Claude Pro/Max plan is required for plan-based usage during the workshop.

## Claude Code

Claude Code supports two ways to authenticate and pay for usage:
- Using your Anthropic API key (pay-per-token)
- Using an Anthropic Claude plan (Pro or Max)

### Setup and Sign-In (Recommended)
- Install the “Claude Code” extension from the VS Code Marketplace.
- Open the Command Palette (`Ctrl/Cmd+Shift+P`) and run: `Claude: Sign in`.
- Log into your Anthropic account and confirm you want to use your plan (Pro/Max) for billing.
- Once signed in, open the Claude view in the activity bar and start a new session.

Note: We do not cover API key setup here. If you need API mode, switch the extension’s authentication to API in its settings and provide your Anthropic API key.

## Codex

Set up both the VS Code extension and the Codex CLI so you can work in-editor or from the terminal.

### VS Code Extension
- In VS Code, open the Extensions view and search for “Codex”.
- Install the “Codex” extension (publisher: OpenAI/OpenAI Labs). 
- After installation, reload the window if prompted and open the Codex panel from the activity bar.

### CLI
- Install the Codex CLI using your preferred method:
  - Download the latest release for your OS from the Codex CLI GitHub releases page, then add the binary to your PATH.
  - Or install via a package manager if provided by your environment (e.g., npm, Homebrew, winget).
- Verify installation:
```bash
codex --version
```

## Qwen Code

Install the official Qwen Code CLI globally via npm:
```bash
npm install -g @qwen-code/qwen-code@latest
```

---

*Last updated: September 2025*
