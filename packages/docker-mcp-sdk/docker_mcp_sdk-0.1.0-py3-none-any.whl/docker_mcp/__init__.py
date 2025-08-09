"""Docker MCP server package.

This package will expose MCP tools to manage Docker containers for safe
code execution. Tests drive the implementation.
"""

from .config import config
from .docker_client import DockerClient
from .container_ops import (
    check_engine,
    list_containers,
    create_container,
    execute_code,
    execute_python_script,
    add_dependencies,
    cleanup_container,
    ToolResult
)

__all__ = [
    "config",
    "DockerClient",
    "check_engine",
    "list_containers",
    "create_container",
    "execute_code",
    "execute_python_script",
    "add_dependencies",
    "cleanup_container",
    "ToolResult"
]

