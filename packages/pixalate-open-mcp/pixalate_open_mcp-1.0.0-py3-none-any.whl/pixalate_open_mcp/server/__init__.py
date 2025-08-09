"""MCP server package initialization"""

from pixalate_open_mcp.config import load_config
from pixalate_open_mcp.server.app import create_mcp_server

# Create server instance with default configuration
server = create_mcp_server(load_config())

__all__ = ["create_mcp_server", "server"]
