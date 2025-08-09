"""Server configuration for pixalate-open-mcp MCP server"""

import os
from dataclasses import dataclass


@dataclass
class ServerConfig:
    """Configuration for the MCP server"""

    name: str = "pixalate-open-mcp"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


def load_config() -> ServerConfig:
    """Load server configuration from environment or defaults"""
    return ServerConfig(
        name=os.getenv("MCP_SERVER_NAME", "pixalate-open-mcp"), log_level=os.getenv("LOG_LEVEL", "INFO")
    )
