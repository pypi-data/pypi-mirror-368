# AI Assistant Setup Instructions for pixalate-open-mcp

This document provides instructions for AI coding assistants to properly configure and use the pixalate-open-mcp MCP server.

## Installation Method

**IMPORTANT**: Use ONLY the isolated `uv tool` installation method to avoid dependency conflicts.

### Step 1: Install the MCP Server

```bash
# Install as an isolated tool (REQUIRED - do not use pip or pipx)
uv tool install .
```

### Step 2: Find the Binary Location

After installation, locate the installed binary path:

**macOS/Linux:**
```bash
which pixalate_open_mcp-server
# Example output: /Users/username/.local/bin/pixalate_open_mcp-server
```

**Windows:**
```bash
where pixalate_open_mcp-server
# Example output: C:\Users\username\.local\bin\pixalate_open_mcp-server.exe
```

### Step 3: Configure Your MCP Client

Use the ABSOLUTE PATH from Step 2 in your configuration:

**For Claude Desktop:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "pixalate_open_mcp": {
      "command": "/absolute/path/to/pixalate_open_mcp-server",
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**For Cline (VS Code):**
Add to `.vscode/settings.json`:

```json
{
  "cline.MCP.mcpServers": {
    "pixalate_open_mcp": {
      "command": "/absolute/path/to/pixalate_open_mcp-server",
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Fallback: Using uvx (Less Reliable)

If `uv tool install` fails, you can use `uvx` as a fallback, but be aware of potential dependency conflicts:

```json
{
  "pixalate_open_mcp": {
    "command": "uvx",
    "args": ["pixalate_open_mcp-server"],
    "env": {
      "API_KEY": "your-api-key-here"
    }
  }
}
```

**WARNING**: The `uvx` method may fail if you have conflicting Python packages installed globally. Always prefer the `uv tool install` method.

## Verification

After configuration:

1. Restart your MCP client
2. Test the connection with: "Use the echo tool to test the connection"
3. If it fails, verify:
   - The binary path is correct and absolute
   - Required environment variables are set
   - No error messages in the MCP client logs

## Troubleshooting

### Binary Not Found
- Ensure `uv` is installed: `pip install uv`
- Verify installation: `uv tool list | grep pixalate_open_mcp`
- Check PATH: The binary location should be in your system PATH

### Dependency Conflicts
- Always use `uv tool install` instead of `pip install`
- If using `uvx` and encountering conflicts, switch to the isolated installation
- Check for conflicting packages: `uv pip list`

### Environment Variables
- Replace `your-api-key-here` with actual credentials
- Ensure no typos in variable names
- Some shells require escaping special characters in API keys
