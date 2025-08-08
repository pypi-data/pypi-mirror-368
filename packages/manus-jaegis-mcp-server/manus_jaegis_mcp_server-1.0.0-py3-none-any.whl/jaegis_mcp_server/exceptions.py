"""
Exception classes for the JAEGIS MCP Server Python wrapper.
"""

class MCPServerError(Exception):
    """Base exception for all MCP server related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class NodeJSNotFoundError(MCPServerError):
    """Raised when Node.js is not found or version is insufficient."""
    
    def __init__(self, message: str = "Node.js not found or version insufficient"):
        super().__init__(message, "NODEJS_NOT_FOUND")

class ServerStartupError(MCPServerError):
    """Raised when the MCP server fails to start."""
    
    def __init__(self, message: str, exit_code: int = None):
        super().__init__(message, "SERVER_STARTUP_ERROR")
        self.exit_code = exit_code

class ServerConnectionError(MCPServerError):
    """Raised when connection to the MCP server fails."""
    
    def __init__(self, message: str, connection_type: str = None):
        super().__init__(message, "SERVER_CONNECTION_ERROR")
        self.connection_type = connection_type

class ToolExecutionError(MCPServerError):
    """Raised when a tool execution fails."""
    
    def __init__(self, message: str, tool_name: str = None, tool_args: dict = None):
        super().__init__(message, "TOOL_EXECUTION_ERROR")
        self.tool_name = tool_name
        self.tool_args = tool_args or {}

class ConfigurationError(MCPServerError):
    """Raised when there's an error with configuration."""
    
    def __init__(self, message: str, config_path: str = None):
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_path = config_path

class DependencyError(MCPServerError):
    """Raised when there's an error with dependencies."""
    
    def __init__(self, message: str, dependency_name: str = None):
        super().__init__(message, "DEPENDENCY_ERROR")
        self.dependency_name = dependency_name

class ValidationError(MCPServerError):
    """Raised when validation fails."""
    
    def __init__(self, message: str, validation_type: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.validation_type = validation_type

class TimeoutError(MCPServerError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str, timeout_duration: float = None):
        super().__init__(message, "TIMEOUT_ERROR")
        self.timeout_duration = timeout_duration

class PermissionError(MCPServerError):
    """Raised when there's a permission error."""
    
    def __init__(self, message: str, resource: str = None):
        super().__init__(message, "PERMISSION_ERROR")
        self.resource = resource
