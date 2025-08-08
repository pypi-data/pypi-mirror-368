"""
JAEGIS MCP Server - Python Package

This package provides a Python wrapper for the JAEGIS MCP Server,
which is implemented in Node.js/TypeScript. The wrapper handles
Node.js execution, dependency management, and provides a Python-friendly
interface for the MCP server.
"""

__version__ = "1.0.0"
__author__ = "JAEGIS Team"
__email__ = "support@jaegis.ai"
__license__ = "MIT"

from .server import MCPServer
from .client import MCPClient
from .exceptions import (
    MCPServerError,
    NodeJSNotFoundError,
    ServerStartupError,
    ServerConnectionError,
    ToolExecutionError
)

__all__ = [
    "MCPServer",
    "MCPClient", 
    "MCPServerError",
    "NodeJSNotFoundError",
    "ServerStartupError",
    "ServerConnectionError",
    "ToolExecutionError",
    "__version__"
]
