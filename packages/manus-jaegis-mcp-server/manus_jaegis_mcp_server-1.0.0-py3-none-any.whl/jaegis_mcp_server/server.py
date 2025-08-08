"""
JAEGIS MCP Server - Python Server Implementation

This module provides the Python wrapper for the JAEGIS MCP Server,
handling Node.js process management and server lifecycle.
"""

import asyncio
import subprocess
import signal
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

from .exceptions import (
    MCPServerError,
    NodeJSNotFoundError,
    ServerStartupError,
    ServerConnectionError
)
from .utils import find_nodejs, check_nodejs_version, get_package_path

logger = logging.getLogger(__name__)

class MCPServer:
    """
    JAEGIS MCP Server wrapper for Python.
    
    This class manages the Node.js MCP server process and provides
    a Python-friendly interface for server management.
    """
    
    def __init__(
        self,
        debug: bool = False,
        config_path: Optional[str] = None,
        port: Optional[int] = None,
        host: str = "localhost",
        transport: str = "stdio"
    ):
        """
        Initialize the MCP Server.
        
        Args:
            debug: Enable debug logging
            config_path: Path to configuration file
            port: Port number for server
            host: Host address for server
            transport: Transport protocol (stdio, sse, websocket)
        """
        self.debug = debug
        self.config_path = config_path
        self.port = port
        self.host = host
        self.transport = transport
        
        self._process: Optional[subprocess.Popen] = None
        self._nodejs_path: Optional[Path] = None
        self._server_script: Optional[Path] = None
        self._running = False
        
        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
    async def start(self) -> None:
        """Start the MCP server."""
        if self._running:
            raise MCPServerError("Server is already running")
        
        logger.info("Starting JAEGIS MCP Server...")
        
        # Find Node.js
        self._nodejs_path = find_nodejs()
        if not self._nodejs_path:
            raise NodeJSNotFoundError("Node.js not found. Please install Node.js 18 or higher.")
        
        # Check Node.js version
        if not check_nodejs_version(self._nodejs_path):
            raise NodeJSNotFoundError("Node.js version 18 or higher is required.")
        
        # Find server script
        package_path = get_package_path()
        self._server_script = package_path / "dist" / "index.js"
        
        if not self._server_script.exists():
            # Try TypeScript source
            self._server_script = package_path / "src" / "index.ts"
            if not self._server_script.exists():
                raise ServerStartupError("Server script not found. Package may be corrupted.")
        
        # Build command
        cmd = self._build_command()
        
        # Set environment
        env = self._build_environment()
        
        try:
            # Start the process
            self._process = subprocess.Popen(
                cmd,
                cwd=package_path,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self._running = True
            logger.info(f"MCP Server started with PID {self._process.pid}")
            
            # Wait a moment to check if process started successfully
            await asyncio.sleep(0.5)
            
            if self._process.poll() is not None:
                # Process has already terminated
                stderr = self._process.stderr.read() if self._process.stderr else ""
                raise ServerStartupError(f"Server failed to start: {stderr}")
                
        except Exception as e:
            self._running = False
            if self._process:
                self._process.terminate()
                self._process = None
            raise ServerStartupError(f"Failed to start server: {e}")
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        if not self._running or not self._process:
            return
        
        logger.info("Stopping JAEGIS MCP Server...")
        
        try:
            # Send SIGTERM first
            self._process.terminate()
            
            # Wait for graceful shutdown
            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process()),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                # Force kill if graceful shutdown failed
                logger.warning("Graceful shutdown timed out, force killing...")
                self._process.kill()
                await asyncio.create_task(self._wait_for_process())
            
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
        finally:
            self._running = False
            self._process = None
            logger.info("MCP Server stopped")
    
    async def restart(self) -> None:
        """Restart the MCP server."""
        await self.stop()
        await self.start()
    
    def is_running(self) -> bool:
        """Check if the server is running."""
        if not self._running or not self._process:
            return False
        
        # Check if process is still alive
        if self._process.poll() is not None:
            self._running = False
            return False
        
        return True
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get information about the server process."""
        if not self._process:
            return {"running": False}
        
        return {
            "running": self.is_running(),
            "pid": self._process.pid if self._process else None,
            "command": self._build_command(),
            "config": {
                "debug": self.debug,
                "config_path": self.config_path,
                "port": self.port,
                "host": self.host,
                "transport": self.transport
            }
        }
    
    async def send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a message to the MCP server.
        
        Args:
            message: JSON-RPC message to send
            
        Returns:
            Response from the server
        """
        if not self.is_running() or not self._process:
            raise ServerConnectionError("Server is not running")
        
        try:
            # Send message
            message_str = json.dumps(message) + "\n"
            self._process.stdin.write(message_str)
            self._process.stdin.flush()
            
            # Read response
            response_str = self._process.stdout.readline()
            if not response_str:
                raise ServerConnectionError("No response from server")
            
            return json.loads(response_str.strip())
            
        except Exception as e:
            raise ServerConnectionError(f"Failed to communicate with server: {e}")
    
    def _build_command(self) -> List[str]:
        """Build the command to start the server."""
        cmd = []
        
        # Use tsx for TypeScript files, node for JavaScript
        if self._server_script.suffix == ".ts":
            cmd = ["npx", "tsx", str(self._server_script)]
        else:
            cmd = [str(self._nodejs_path), str(self._server_script)]
        
        # Add arguments
        if self.debug:
            cmd.append("--debug")
        if self.config_path:
            cmd.extend(["--config", self.config_path])
        if self.port:
            cmd.extend(["--port", str(self.port)])
        if self.host != "localhost":
            cmd.extend(["--host", self.host])
        if self.transport != "stdio":
            cmd.extend(["--transport", self.transport])
        
        return cmd
    
    def _build_environment(self) -> Dict[str, str]:
        """Build environment variables for the server."""
        env = os.environ.copy()
        
        if self.debug:
            env["JAEGIS_MCP_DEBUG"] = "true"
        if self.port:
            env["JAEGIS_MCP_PORT"] = str(self.port)
        if self.host:
            env["JAEGIS_MCP_HOST"] = self.host
        if self.config_path:
            env["JAEGIS_MCP_CONFIG"] = self.config_path
        
        # Ensure colored output
        env["FORCE_COLOR"] = "1"
        
        return env
    
    async def _wait_for_process(self) -> None:
        """Wait for the process to terminate."""
        if self._process:
            while self._process.poll() is None:
                await asyncio.sleep(0.1)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    def client(self):
        """Get a client for this server."""
        from .client import MCPClient
        return MCPClient(server=self)
