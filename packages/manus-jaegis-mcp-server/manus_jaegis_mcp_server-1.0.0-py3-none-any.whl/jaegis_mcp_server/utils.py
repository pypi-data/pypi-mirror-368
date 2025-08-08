"""
Utility functions for the JAEGIS MCP Server Python wrapper.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import json

def find_nodejs() -> Optional[Path]:
    """
    Find Node.js executable on the system.
    
    Returns:
        Path to Node.js executable or None if not found
    """
    # Common Node.js executable names
    node_names = ["node", "nodejs"]
    
    # On Windows, add .exe extension
    if platform.system() == "Windows":
        node_names.extend(["node.exe", "nodejs.exe"])
    
    # Try to find Node.js in PATH
    for name in node_names:
        node_path = shutil.which(name)
        if node_path:
            return Path(node_path)
    
    # Try common installation paths
    common_paths = []
    
    if platform.system() == "Windows":
        common_paths.extend([
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "node.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs" / "node.exe",
            Path.home() / "AppData" / "Roaming" / "npm" / "node.exe",
        ])
    elif platform.system() == "Darwin":  # macOS
        common_paths.extend([
            Path("/usr/local/bin/node"),
            Path("/opt/homebrew/bin/node"),
            Path("/usr/bin/node"),
        ])
    else:  # Linux and other Unix-like systems
        common_paths.extend([
            Path("/usr/bin/node"),
            Path("/usr/local/bin/node"),
            Path("/opt/node/bin/node"),
        ])
    
    # Check common paths
    for path in common_paths:
        if path.exists() and path.is_file():
            return path
    
    return None

def check_nodejs_version(nodejs_path: Union[str, Path], min_version: str = "18.0.0") -> bool:
    """
    Check if Node.js version meets minimum requirements.
    
    Args:
        nodejs_path: Path to Node.js executable
        min_version: Minimum required version (default: "18.0.0")
    
    Returns:
        True if version is sufficient, False otherwise
    """
    try:
        result = subprocess.run(
            [str(nodejs_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False
        
        # Parse version string (e.g., "v18.17.0" -> "18.17.0")
        version_str = result.stdout.strip()
        if version_str.startswith("v"):
            version_str = version_str[1:]
        
        # Simple version comparison (assumes semantic versioning)
        current_parts = [int(x) for x in version_str.split(".")]
        min_parts = [int(x) for x in min_version.split(".")]
        
        # Pad shorter version with zeros
        max_len = max(len(current_parts), len(min_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        min_parts.extend([0] * (max_len - len(min_parts)))
        
        return current_parts >= min_parts
        
    except Exception:
        return False

def get_package_path() -> Path:
    """
    Get the path to the package directory containing the Node.js server.
    
    Returns:
        Path to the package directory
    """
    # Get the directory containing this Python file
    current_dir = Path(__file__).parent
    
    # Look for package.json in various locations
    search_paths = [
        current_dir,  # Same directory as Python package
        current_dir.parent,  # Parent directory
        current_dir.parent.parent,  # Grandparent directory
        current_dir / "nodejs",  # nodejs subdirectory
        current_dir / "server",  # server subdirectory
    ]
    
    for path in search_paths:
        package_json = path / "package.json"
        if package_json.exists():
            return path
    
    # If not found, return the current directory
    return current_dir

def check_npm_package_installed(package_name: str) -> bool:
    """
    Check if an npm package is installed globally.
    
    Args:
        package_name: Name of the npm package
    
    Returns:
        True if package is installed, False otherwise
    """
    try:
        result = subprocess.run(
            ["npm", "list", "-g", package_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception:
        return False

def install_npm_package_global(package_name: str) -> bool:
    """
    Install an npm package globally.
    
    Args:
        package_name: Name of the npm package to install
    
    Returns:
        True if installation succeeded, False otherwise
    """
    try:
        result = subprocess.run(
            ["npm", "install", "-g", package_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )
        return result.returncode == 0
    except Exception:
        return False

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary containing system information
    """
    info = {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "nodejs": {
            "available": False,
            "path": None,
            "version": None,
        },
        "npm": {
            "available": False,
            "path": None,
            "version": None,
        },
        "environment": {
            "path": os.environ.get("PATH", ""),
            "home": str(Path.home()),
            "cwd": str(Path.cwd()),
        }
    }
    
    # Check Node.js
    nodejs_path = find_nodejs()
    if nodejs_path:
        info["nodejs"]["available"] = True
        info["nodejs"]["path"] = str(nodejs_path)
        
        try:
            result = subprocess.run(
                [str(nodejs_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                info["nodejs"]["version"] = result.stdout.strip()
        except Exception:
            pass
    
    # Check npm
    npm_path = shutil.which("npm")
    if npm_path:
        info["npm"]["available"] = True
        info["npm"]["path"] = npm_path
        
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                info["npm"]["version"] = result.stdout.strip()
        except Exception:
            pass
    
    return info

def validate_config_file(config_path: Union[str, Path]) -> bool:
    """
    Validate MCP server configuration file.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        config_path = Path(config_path)
        
        if not config_path.exists():
            return False
        
        # Try to parse as JSON
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Basic validation - check for required fields
        required_fields = ["server"]
        for field in required_fields:
            if field not in config:
                return False
        
        return True
        
    except Exception:
        return False

def create_default_config(config_path: Union[str, Path]) -> bool:
    """
    Create a default configuration file.
    
    Args:
        config_path: Path where to create the configuration file
    
    Returns:
        True if configuration was created successfully, False otherwise
    """
    try:
        config_path = Path(config_path)
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            "server": {
                "name": "jaegis-mcp-server",
                "version": "1.0.0",
                "debug": False
            },
            "tools": {
                "filesystem": {
                    "enabled": True,
                    "maxFileSize": "10MB",
                    "allowedExtensions": ["*"]
                },
                "git": {
                    "enabled": True,
                    "autoCommit": False
                },
                "project": {
                    "enabled": True,
                    "defaultFramework": "nodejs"
                },
                "ai": {
                    "enabled": True,
                    "provider": "openai"
                }
            },
            "security": {
                "allowFileOperations": True,
                "allowGitOperations": True,
                "sandboxMode": False
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        return True
        
    except Exception:
        return False

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def is_port_available(port: int, host: str = "localhost") -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        port: Port number to check
        host: Host address to check (default: localhost)
    
    Returns:
        True if port is available, False otherwise
    """
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except Exception:
        return False
