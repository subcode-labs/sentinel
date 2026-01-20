# Sentinel MCP Server

This package implements a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Sentinel. It allows AI assistants (like Claude Desktop) to securely access secrets managed by Sentinel.

## Installation

This package is currently part of the Sentinel repository. To use it, you need to build it locally.

```bash
cd sentinel/examples/mcp-server
npm install
npm run build
```

## Configuration (Claude Desktop)

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sentinel": {
      "command": "node",
      "args": ["/path/to/sentinel/examples/mcp-server/dist/index.js"],
      "env": {
        "SENTINEL_TOKEN": "sat_your_access_token_here",
        "SENTINEL_PROJECT": "your-project-slug",
        "SENTINEL_ENV": "dev"
      }
    }
  }
}
```

## Tools

### `list_secrets`
Lists available secret keys in a project environment.

**Arguments:**
- `project`: Project slug
- `environment`: Environment slug

### `get_secret`
Retrieves the value of a specific secret.

**Arguments:**
- `project`: Project slug
- `environment`: Environment slug
- `key`: Secret key name
