"""
JAEGIS MCP Client - Python Client Implementation

This module provides a Python client for communicating with the JAEGIS MCP Server.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List, Union
import logging

from .exceptions import (
    MCPServerError,
    ServerConnectionError,
    ToolExecutionError
)

logger = logging.getLogger(__name__)

class MCPClient:
    """
    JAEGIS MCP Client for Python.
    
    This class provides a Python interface for communicating with
    the JAEGIS MCP Server using the Model Context Protocol.
    """
    
    def __init__(self, server=None, timeout: float = 30.0):
        """
        Initialize the MCP Client.
        
        Args:
            server: MCPServer instance to connect to
            timeout: Default timeout for requests
        """
        self.server = server
        self.timeout = timeout
        self._connected = False
        self._request_id = 0
        
    async def connect(self) -> None:
        """Connect to the MCP server."""
        if not self.server:
            raise ServerConnectionError("No server instance provided")
        
        if not self.server.is_running():
            raise ServerConnectionError("Server is not running")
        
        # Send initialize request
        response = await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "jaegis-mcp-client-python",
                "version": "1.0.0"
            }
        })
        
        if "error" in response:
            raise ServerConnectionError(f"Failed to initialize: {response['error']}")
        
        self._connected = True
        logger.info("Connected to MCP server")
    
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self._connected:
            try:
                await self._send_notification("notifications/cancelled", {})
            except Exception:
                pass  # Ignore errors during disconnect
        
        self._connected = False
        logger.info("Disconnected from MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the server.
        
        Returns:
            List of tool definitions
        """
        if not self._connected:
            raise ServerConnectionError("Not connected to server")
        
        response = await self._send_request("tools/list", {})
        
        if "error" in response:
            raise MCPServerError(f"Failed to list tools: {response['error']}")
        
        return response.get("result", {}).get("tools", [])
    
    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Any:
        """
        Call a tool on the server.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            timeout: Request timeout (uses default if None)
            
        Returns:
            Tool execution result
        """
        if not self._connected:
            raise ServerConnectionError("Not connected to server")
        
        request_timeout = timeout or self.timeout
        
        try:
            response = await asyncio.wait_for(
                self._send_request("tools/call", {
                    "name": name,
                    "arguments": arguments
                }),
                timeout=request_timeout
            )
            
            if "error" in response:
                error_info = response["error"]
                raise ToolExecutionError(
                    f"Tool '{name}' failed: {error_info.get('message', 'Unknown error')}",
                    tool_name=name,
                    tool_args=arguments
                )
            
            return response.get("result", {})
            
        except asyncio.TimeoutError:
            raise ToolExecutionError(
                f"Tool '{name}' timed out after {request_timeout} seconds",
                tool_name=name,
                tool_args=arguments
            )
        except Exception as e:
            raise ToolExecutionError(
                f"Tool '{name}' execution failed: {e}",
                tool_name=name,
                tool_args=arguments
            )
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List available resources from the server.
        
        Returns:
            List of resource definitions
        """
        if not self._connected:
            raise ServerConnectionError("Not connected to server")
        
        response = await self._send_request("resources/list", {})
        
        if "error" in response:
            raise MCPServerError(f"Failed to list resources: {response['error']}")
        
        return response.get("result", {}).get("resources", [])
    
    async def read_resource(
        self,
        uri: str,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Read a resource from the server.
        
        Args:
            uri: Resource URI
            timeout: Request timeout (uses default if None)
            
        Returns:
            Resource content
        """
        if not self._connected:
            raise ServerConnectionError("Not connected to server")
        
        request_timeout = timeout or self.timeout
        
        try:
            response = await asyncio.wait_for(
                self._send_request("resources/read", {
                    "uri": uri
                }),
                timeout=request_timeout
            )
            
            if "error" in response:
                error_info = response["error"]
                raise MCPServerError(
                    f"Failed to read resource '{uri}': {error_info.get('message', 'Unknown error')}"
                )
            
            return response.get("result", {})
            
        except asyncio.TimeoutError:
            raise MCPServerError(f"Resource read timed out after {request_timeout} seconds")
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List available prompts from the server.
        
        Returns:
            List of prompt definitions
        """
        if not self._connected:
            raise ServerConnectionError("Not connected to server")
        
        response = await self._send_request("prompts/list", {})
        
        if "error" in response:
            raise MCPServerError(f"Failed to list prompts: {response['error']}")
        
        return response.get("result", {}).get("prompts", [])
    
    async def get_prompt(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get a prompt from the server.
        
        Args:
            name: Prompt name
            arguments: Prompt arguments
            timeout: Request timeout (uses default if None)
            
        Returns:
            Prompt content
        """
        if not self._connected:
            raise ServerConnectionError("Not connected to server")
        
        request_timeout = timeout or self.timeout
        arguments = arguments or {}
        
        try:
            response = await asyncio.wait_for(
                self._send_request("prompts/get", {
                    "name": name,
                    "arguments": arguments
                }),
                timeout=request_timeout
            )
            
            if "error" in response:
                error_info = response["error"]
                raise MCPServerError(
                    f"Failed to get prompt '{name}': {error_info.get('message', 'Unknown error')}"
                )
            
            return response.get("result", {})
            
        except asyncio.TimeoutError:
            raise MCPServerError(f"Prompt request timed out after {request_timeout} seconds")
    
    async def _send_request(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the server.
        
        Args:
            method: RPC method name
            params: Method parameters
            
        Returns:
            Server response
        """
        if not self.server:
            raise ServerConnectionError("No server instance")
        
        self._request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params
        }
        
        return await self.server.send_message(request)
    
    async def _send_notification(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> None:
        """
        Send a JSON-RPC notification to the server.
        
        Args:
            method: RPC method name
            params: Method parameters
        """
        if not self.server:
            raise ServerConnectionError("No server instance")
        
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        await self.server.send_message(notification)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

# Convenience functions for common operations
async def list_available_tools(server=None) -> List[str]:
    """
    Get a list of available tool names.
    
    Args:
        server: MCPServer instance (optional)
        
    Returns:
        List of tool names
    """
    client = MCPClient(server)
    async with client:
        tools = await client.list_tools()
        return [tool["name"] for tool in tools]

async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    server=None,
    timeout: float = 30.0
) -> Any:
    """
    Execute a tool with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        server: MCPServer instance (optional)
        timeout: Request timeout
        
    Returns:
        Tool execution result
    """
    client = MCPClient(server, timeout=timeout)
    async with client:
        return await client.call_tool(tool_name, arguments, timeout)
