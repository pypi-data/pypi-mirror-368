#!/usr/bin/env python3
"""
JAEGIS MCP Server - Python CLI

This module provides the command-line interface for the Python wrapper
of the JAEGIS MCP Server. It handles Node.js execution, argument parsing,
and provides a seamless experience for Python users.
"""

import sys
import os
import subprocess
import shutil
import json
import platform
from pathlib import Path
from typing import List, Optional, Dict, Any
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from . import __version__
from .exceptions import NodeJSNotFoundError, ServerStartupError
from .utils import find_nodejs, check_nodejs_version, get_package_path

console = Console()

def show_banner():
    """Display the JAEGIS MCP Server banner."""
    banner_text = Text()
    banner_text.append("JAEGIS MCP SERVER\n", style="bold cyan")
    banner_text.append("Model Context Protocol Server\n", style="cyan")
    banner_text.append(f"Version: {__version__}\n", style="dim")
    banner_text.append("Python Wrapper for Node.js Implementation", style="dim")
    
    panel = Panel(
        banner_text,
        title="🤖 JAEGIS AI Web OS",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)

def check_dependencies() -> Dict[str, Any]:
    """Check system dependencies and return status."""
    status = {
        "nodejs": {"available": False, "version": None, "path": None},
        "npm": {"available": False, "version": None, "path": None},
        "npx": {"available": False, "version": None, "path": None},
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python_version": platform.python_version()
        }
    }
    
    # Check Node.js
    try:
        nodejs_path = find_nodejs()
        if nodejs_path:
            status["nodejs"]["available"] = True
            status["nodejs"]["path"] = str(nodejs_path)
            
            # Get Node.js version
            result = subprocess.run(
                [str(nodejs_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                status["nodejs"]["version"] = result.stdout.strip()
    except Exception:
        pass
    
    # Check npm
    npm_path = shutil.which("npm")
    if npm_path:
        status["npm"]["available"] = True
        status["npm"]["path"] = npm_path
        
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                status["npm"]["version"] = result.stdout.strip()
        except Exception:
            pass
    
    # Check npx
    npx_path = shutil.which("npx")
    if npx_path:
        status["npx"]["available"] = True
        status["npx"]["path"] = npx_path
        
        try:
            result = subprocess.run(
                ["npx", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                status["npx"]["version"] = result.stdout.strip()
        except Exception:
            pass
    
    return status

def install_nodejs_dependencies() -> bool:
    """Install Node.js dependencies for the MCP server."""
    try:
        package_path = get_package_path()
        package_json_path = package_path / "package.json"
        
        if not package_json_path.exists():
            console.print("[red]Error: package.json not found in package directory[/red]")
            return False
        
        console.print("[blue]Installing Node.js dependencies...[/blue]")
        
        # Run npm install in the package directory
        result = subprocess.run(
            ["npm", "install", "--production"],
            cwd=package_path,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            console.print("[green]✓ Dependencies installed successfully[/green]")
            return True
        else:
            console.print(f"[red]✗ Failed to install dependencies: {result.stderr}[/red]")
            return False
            
    except subprocess.TimeoutExpired:
        console.print("[red]✗ Timeout while installing dependencies[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Error installing dependencies: {e}[/red]")
        return False

def start_nodejs_server(args: List[str]) -> int:
    """Start the Node.js MCP server with the given arguments."""
    try:
        # Find Node.js executable
        nodejs_path = find_nodejs()
        if not nodejs_path:
            raise NodeJSNotFoundError("Node.js not found. Please install Node.js 18 or higher.")
        
        # Check Node.js version
        if not check_nodejs_version(nodejs_path):
            raise NodeJSNotFoundError("Node.js version 18 or higher is required.")
        
        # Get package path and server script
        package_path = get_package_path()
        server_script = package_path / "dist" / "index.js"
        
        # If dist doesn't exist, try to use the TypeScript source
        if not server_script.exists():
            server_script = package_path / "src" / "index.ts"
            if server_script.exists():
                # Use tsx to run TypeScript directly
                cmd = ["npx", "tsx", str(server_script)] + args
            else:
                raise ServerStartupError("Server script not found. Package may be corrupted.")
        else:
            cmd = [str(nodejs_path), str(server_script)] + args
        
        console.print(f"[blue]Starting JAEGIS MCP Server...[/blue]")
        console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")
        
        # Start the server process
        process = subprocess.Popen(
            cmd,
            cwd=package_path,
            env={**os.environ, "FORCE_COLOR": "1"},
            stdout=sys.stdout,
            stderr=sys.stderr,
            stdin=sys.stdin
        )
        
        # Wait for the process to complete
        return process.wait()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        return 1

@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version information")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(exists=True), help="Configuration file path")
@click.option("--port", type=int, help="Port number")
@click.option("--host", help="Host address")
@click.option("--stdio", "transport", flag_value="stdio", default=True, help="Use stdio transport")
@click.option("--sse", "transport", flag_value="sse", help="Use Server-Sent Events transport")
@click.option("--websocket", "transport", flag_value="websocket", help="Use WebSocket transport")
@click.pass_context
def cli(ctx, version, debug, config, port, host, transport):
    """JAEGIS MCP Server - Python wrapper for Node.js implementation."""
    
    if version:
        console.print(f"JAEGIS MCP Server v{__version__} (Python wrapper)")
        return
    
    # If no subcommand is provided, start the server
    if ctx.invoked_subcommand is None:
        show_banner()
        
        # Build arguments for the Node.js server
        args = []
        if debug:
            args.append("--debug")
        if config:
            args.extend(["--config", config])
        if port:
            args.extend(["--port", str(port)])
        if host:
            args.extend(["--host", host])
        if transport != "stdio":
            args.extend(["--transport", transport])
        
        # Start the server
        exit_code = start_nodejs_server(args)
        sys.exit(exit_code)

@cli.command()
def status():
    """Check system status and dependencies."""
    show_banner()
    
    console.print("[bold]System Status Check[/bold]\n")
    
    status = check_dependencies()
    
    # Platform information
    platform_info = status["platform"]
    console.print(f"[cyan]Platform:[/cyan] {platform_info['system']} {platform_info['machine']}")
    console.print(f"[cyan]Python:[/cyan] {platform_info['python_version']}\n")
    
    # Node.js status
    nodejs_status = status["nodejs"]
    if nodejs_status["available"]:
        console.print(f"[green]✓ Node.js:[/green] {nodejs_status['version']} ({nodejs_status['path']})")
    else:
        console.print("[red]✗ Node.js: Not found[/red]")
    
    # npm status
    npm_status = status["npm"]
    if npm_status["available"]:
        console.print(f"[green]✓ npm:[/green] {npm_status['version']} ({npm_status['path']})")
    else:
        console.print("[red]✗ npm: Not found[/red]")
    
    # npx status
    npx_status = status["npx"]
    if npx_status["available"]:
        console.print(f"[green]✓ npx:[/green] {npx_status['version']} ({npx_status['path']})")
    else:
        console.print("[red]✗ npx: Not found[/red]")
    
    # Overall status
    console.print()
    if all([nodejs_status["available"], npm_status["available"], npx_status["available"]]):
        console.print("[green]✓ All dependencies are available[/green]")
    else:
        console.print("[red]✗ Some dependencies are missing[/red]")
        console.print("\n[yellow]To install Node.js, visit: https://nodejs.org/[/yellow]")

@cli.command()
def install():
    """Install Node.js dependencies."""
    show_banner()
    
    console.print("[bold]Installing Dependencies[/bold]\n")
    
    # Check if Node.js is available
    status = check_dependencies()
    if not status["nodejs"]["available"]:
        console.print("[red]Error: Node.js is required but not found[/red]")
        console.print("Please install Node.js 18 or higher from: https://nodejs.org/")
        sys.exit(1)
    
    if not status["npm"]["available"]:
        console.print("[red]Error: npm is required but not found[/red]")
        sys.exit(1)
    
    # Install dependencies
    if install_nodejs_dependencies():
        console.print("\n[green]✓ Installation completed successfully[/green]")
    else:
        console.print("\n[red]✗ Installation failed[/red]")
        sys.exit(1)

@cli.command()
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text")
def info(output_format):
    """Show detailed system information."""
    status = check_dependencies()
    
    if output_format == "json":
        click.echo(json.dumps(status, indent=2))
    else:
        show_banner()
        console.print("[bold]System Information[/bold]\n")
        
        # Create a formatted table-like output
        info_data = [
            ("Python Version", status["platform"]["python_version"]),
            ("Platform", f"{status['platform']['system']} {status['platform']['machine']}"),
            ("Node.js", f"{status['nodejs']['version'] if status['nodejs']['available'] else 'Not found'}"),
            ("npm", f"{status['npm']['version'] if status['npm']['available'] else 'Not found'}"),
            ("npx", f"{status['npx']['version'] if status['npx']['available'] else 'Not found'}"),
            ("Package Version", __version__)
        ]
        
        for key, value in info_data:
            console.print(f"[cyan]{key:15}:[/cyan] {value}")

def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if os.getenv("JAEGIS_MCP_DEBUG") == "true":
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
