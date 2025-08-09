"""MCP server implementation for Docker container operations."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from . import container_ops

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("docker-mcp")


@mcp.tool()
async def check_engine() -> str:
    """Check Docker engine availability and version.
    
    Returns a summary of Docker engine status.
    """
    result = await asyncio.to_thread(container_ops.check_engine)
    return f"{result.text}\n\nData: {result.data}"


@mcp.tool()
async def list_containers(show_all: bool = False, session_id: Optional[str] = None) -> str:
    """List Docker containers.
    
    Args:
        show_all: Show all containers (not just running ones)
        session_id: Filter by session ID
    
    Returns a list of containers with their details.
    """
    result = await asyncio.to_thread(
        container_ops.list_containers,
        show_all=show_all,
        session_id=session_id
    )
    return f"{result.text}\n\nContainers: {result.data}"


@mcp.tool()
async def create_container(
    image: str,
    name: Optional[str] = None,
    dependencies: Optional[str] = None,
    network_enabled: bool = False,
    session_id: Optional[str] = None,
    reuse_existing: bool = False,
    environment: Optional[Dict[str, str]] = None
) -> str:
    """Create and start a new Docker container.
    
    Args:
        image: Docker image to use (e.g., 'python:3.11-slim')
        name: Optional container name
        dependencies: Comma-separated list of packages to install
        network_enabled: Enable network access
        session_id: Session ID for container grouping
        reuse_existing: Reuse existing container if available
        environment: Environment variables
    
    Returns container creation status and ID.
    """
    result = await asyncio.to_thread(
        container_ops.create_container,
        image=image,
        container_name=name,
        dependencies=dependencies or "",
        network="bridge" if network_enabled else "none",
        session_id=session_id,
        reuse_existing=reuse_existing,
        environment=environment
    )
    return f"{result.text}\n\nContainer Info: {result.data}"


@mcp.tool()
async def execute_code(
    container_id: str,
    command: str,
    timeout: int = 120,
    stream: bool = False,
    working_dir: str = "/workspace"
) -> str:
    """Execute a command in a running container.
    
    Args:
        container_id: Container ID or name
        command: Command to execute
        timeout: Execution timeout in seconds
        stream: Stream output
        working_dir: Working directory
    
    Returns command output and exit code.
    """
    result = await asyncio.to_thread(
        container_ops.execute_code,
        container_name=container_id,
        command=command,
        timeout=timeout,
        stream=stream,
        working_dir=working_dir
    )
    
    output = result.data
    response_text = f"{result.text}\n"
    if 'stdout' in output:
        response_text += f"\nStdout:\n{output['stdout']}"
    if 'stderr' in output and output['stderr']:
        response_text += f"\nStderr:\n{output['stderr']}"
    if 'exit_code' in output:
        response_text += f"\nExit Code: {output['exit_code']}"
    
    return response_text


@mcp.tool()
async def execute_python_script(
    container_id: str,
    script: str,
    args: Optional[List[str]] = None,
    timeout: int = 180,
    packages: Optional[List[str]] = None
) -> str:
    """Execute a Python script in a container.
    
    Args:
        container_id: Container ID or name
        script: Python script content
        args: Script arguments
        timeout: Execution timeout in seconds
        packages: Python packages to install first
    
    Returns script output and exit code.
    """
    result = await asyncio.to_thread(
        container_ops.execute_python_script,
        container_name=container_id,
        script_content=script,
        script_args=" ".join(args) if args else "",
        timeout=timeout,
        packages=packages
    )
    
    output = result.data
    response_text = f"{result.text}\n"
    if 'stdout' in output:
        response_text += f"\nOutput:\n{output['stdout']}"
    if 'stderr' in output and output['stderr']:
        response_text += f"\nErrors:\n{output['stderr']}"
    if 'exit_code' in output:
        response_text += f"\nExit Code: {output['exit_code']}"
    
    return response_text


@mcp.tool()
async def add_dependencies(
    container_id: str,
    packages: List[str],
    package_manager: Optional[str] = None
) -> str:
    """Install packages in a running container.
    
    Args:
        container_id: Container ID or name
        packages: List of packages to install
        package_manager: Package manager (pip, npm, apt, apk)
    
    Returns installation status.
    """
    result = await asyncio.to_thread(
        container_ops.add_dependencies,
        container_name=container_id,
        dependencies=",".join(packages),
        package_manager=package_manager
    )
    return f"{result.text}\n\nDetails: {result.data}"


@mcp.tool()
async def cleanup_container(
    container_id: Optional[str] = None,
    session_id: Optional[str] = None,
    cleanup_all: bool = False,
    remove_volumes: bool = False
) -> str:
    """Stop and remove containers.
    
    Args:
        container_id: Specific container to remove
        session_id: Remove all containers for a session
        cleanup_all: Remove all MCP-managed containers
        remove_volumes: Also remove associated volumes
    
    Returns cleanup status.
    """
    result = await asyncio.to_thread(
        container_ops.cleanup_container,
        container_name=container_id,
        session_id=session_id,
        cleanup_all=cleanup_all,
        remove_volume=remove_volumes
    )
    return f"{result.text}\n\nDetails: {result.data}"


def main():
    """Main entry point."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()