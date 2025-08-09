from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, List

from docker.errors import DockerException, ContainerError, ImageNotFound

from .docker_client import DockerClient
from .config import config


@dataclass
class ToolResult:
    text: str
    data: Any


def list_containers(*, client: Any = None, show_all: bool = True, session_id: Optional[str] = None) -> ToolResult:
    """List docker containers.

    Returns ToolResult with text summary and data list of container dicts.
    """
    try:
        docker_client = client or DockerClient()
        
        # Build filters
        filters = None
        if session_id:
            filters = {'label': f'mcp-session={session_id}'}
        
        containers = docker_client.list_containers(all=show_all, filters=filters)
        
        if not containers:
            return ToolResult(
                text="No containers found",
                data=[]
            )
        
        # Format container data
        formatted_containers = []
        for container in containers:
            formatted_containers.append({
                'id': container['id'][:12],  # Short ID
                'name': container['name'],
                'image': container['image'],
                'status': container['status'],
                'created': container['created'],
                'state': container['state'],
                'labels': container.get('labels', {})
            })
        
        text = f"Listed {len(formatted_containers)} container(s)"
        if session_id:
            text += f" for session {session_id}"
        
        return ToolResult(
            text=text,
            data=formatted_containers
        )
    except Exception as e:
        return ToolResult(
            text=f"Failed to list containers: {str(e)}",
            data=[]
        )


def create_container(
    *,
    client: Any = None,
    image: str,
    container_name: Optional[str] = None,
    dependencies: str = "",
    network: str = "none",
    memory: Optional[str] = None,
    cpus: Optional[float] = None,
    pids_limit: Optional[int] = None,
    session_id: Optional[str] = None,
    reuse_existing: bool = False,
    environment: Optional[Dict[str, str]] = None,
) -> ToolResult:
    """Create and start a container with optional dependencies."""
    try:
        docker_client = client or DockerClient()
        
        # Check if we should reuse existing container
        if reuse_existing and session_id:
            try:
                container_id = docker_client.get_or_create_container(
                    image=image,
                    session_id=session_id,
                    name=container_name,
                    network_enabled=(network != "none"),
                    environment=environment
                )
                return ToolResult(
                    text=f"Reused existing container {container_id[:12]} for session {session_id}",
                    data={'container_id': container_id, 'reused': True}
                )
            except Exception:
                pass  # Fall through to create new container
        
        # Check if image exists, pull if needed
        if not docker_client.image_exists(image):
            docker_client.pull_image(image)
        
        # Generate container name if not provided
        if not container_name:
            import uuid
            container_name = f"mcp-{image.split(':')[0].split('/')[-1]}-{uuid.uuid4().hex[:8]}"
        
        # Create container
        container_id = docker_client.create_container(
            image=image,
            name=container_name,
            network_enabled=(network != "none"),
            session_id=session_id,
            persist_workspace=(session_id is not None),
            environment=environment
        )
        
        # Start container
        docker_client.start_container(container_id)
        
        # Wait for container to be ready
        if not docker_client.wait_for_ready(container_id):
            return ToolResult(
                text=f"Container created but not ready: {container_id[:12]}",
                data={'container_id': container_id, 'ready': False}
            )
        
        # Install dependencies if provided
        if dependencies:
            deps_result = add_dependencies(
                client=docker_client,
                container_name=container_id,
                dependencies=dependencies
            )
            if "Failed" in deps_result.text:
                return ToolResult(
                    text=f"Container created but dependency installation failed: {deps_result.text}",
                    data={'container_id': container_id, 'dependencies_installed': False}
                )
        
        return ToolResult(
            text=f"Container {container_name} ({container_id[:12]}) created and started successfully",
            data={'container_id': container_id, 'name': container_name, 'ready': True}
        )
    except Exception as e:
        return ToolResult(
            text=f"Failed to create container: {str(e)}",
            data={'error': str(e)}
        )


def add_dependencies(
    *, 
    client: Any = None, 
    container_name: str, 
    dependencies: str, 
    language: Optional[str] = None, 
    package_manager: Optional[str] = None
) -> ToolResult:
    """Install additional dependencies in a running container."""
    try:
        docker_client = client or DockerClient()
        
        # Determine package manager if not specified
        if not package_manager:
            if language == "python":
                package_manager = "pip"
            elif language == "node" or language == "javascript":
                package_manager = "npm"
            else:
                # Try to detect from container
                for pm in ['pip', 'npm', 'apt', 'apk']:
                    check_cmd = {
                        'pip': 'which pip',
                        'npm': 'which npm',
                        'apt': 'which apt-get',
                        'apk': 'which apk'
                    }[pm]
                    
                    result = docker_client.execute_command(container_name, check_cmd)
                    if result['exit_code'] == 0:
                        package_manager = pm
                        break
        
        if not package_manager:
            return ToolResult(
                text="Could not determine package manager",
                data={'error': 'No package manager found'}
            )
        
        # Update package manager if needed
        if package_manager == 'apt':
            docker_client.execute_command(container_name, 'apt-get update')
        elif package_manager == 'apk':
            docker_client.execute_command(container_name, 'apk update')
        
        # Parse dependencies
        dep_list = [d.strip() for d in dependencies.split(',') if d.strip()]
        
        installed = []
        failed = []
        
        for dep in dep_list:
            result = docker_client.install_package(
                container_name,
                dep,
                package_manager
            )
            
            if result['success']:
                installed.append(dep)
            else:
                failed.append(dep)
        
        if failed:
            return ToolResult(
                text=f"Failed to install some packages: {', '.join(failed)}",
                data={'installed': installed, 'failed': failed}
            )
        
        return ToolResult(
            text=f"Successfully installed {len(installed)} package(s) using {package_manager}",
            data={'installed': installed, 'package_manager': package_manager}
        )
    except Exception as e:
        return ToolResult(
            text=f"Failed to add dependencies: {str(e)}",
            data={'error': str(e)}
        )


def execute_code(
    *,
    client: Any = None,
    container_name: str,
    command: str,
    timeout: int = 120,
    env: Optional[Dict[str, str]] = None,
    max_output_bytes: Optional[int] = None,
    stream: bool = False,
    working_dir: str = '/workspace'
) -> ToolResult:
    """Execute a command inside a running container."""
    try:
        docker_client = client or DockerClient()
        
        # Add timeout to command if specified
        if timeout and timeout < config.timeout:
            command = f"timeout {timeout} {command}"
        
        # Execute command
        start_time = time.time()
        
        if stream:
            # Streaming execution returns a generator - collect all output
            output_bytes = 0
            stdout_lines = []
            stderr_lines = []
            
            try:
                for chunk in docker_client.execute_command(
                    container_name, 
                    command, 
                    stream=True,
                    workdir=working_dir
                ):
                    if chunk.get('stdout'):
                        stdout_lines.append(chunk['stdout'])
                        output_bytes += len(chunk['stdout'])
                    
                    if chunk.get('stderr'):
                        stderr_lines.append(chunk['stderr'])
                        output_bytes += len(chunk['stderr'])
                    
                    # Check output size limit
                    if max_output_bytes and output_bytes > max_output_bytes:
                        return ToolResult(
                            text="Output exceeded maximum size limit",
                            data={
                                'stdout': ''.join(stdout_lines)[:max_output_bytes],
                                'stderr': ''.join(stderr_lines),
                                'truncated': True
                            }
                        )
                    
                    # Check timeout
                    if time.time() - start_time > timeout:
                        docker_client.kill_process(container_name, command.split()[0])
                        return ToolResult(
                            text=f"Command timed out after {timeout} seconds",
                            data={
                                'stdout': ''.join(stdout_lines),
                                'stderr': ''.join(stderr_lines),
                                'timed_out': True
                            }
                        )
                
                return ToolResult(
                    text="Command executed successfully (streaming)",
                    data={
                        'stdout': ''.join(stdout_lines),
                        'stderr': ''.join(stderr_lines),
                        'exit_code': 0
                    }
                )
            except Exception as e:
                return ToolResult(
                    text=f"Streaming execution failed: {str(e)}",
                    data={
                        'stdout': ''.join(stdout_lines),
                        'stderr': ''.join(stderr_lines) + str(e),
                        'error': str(e)
                    }
                )
        else:
            # Non-streaming execution
            result = docker_client.execute_command(
                container_name,
                command,
                workdir=working_dir
            )
            
            # Check output size
            if max_output_bytes:
                if len(result['stdout']) > max_output_bytes:
                    result['stdout'] = result['stdout'][:max_output_bytes]
                    result['truncated'] = True
            
            if result['exit_code'] == 0:
                return ToolResult(
                    text="Command executed successfully",
                    data=result
                )
            elif result['exit_code'] == 124:
                return ToolResult(
                    text=f"Command timed out after {timeout} seconds",
                    data={**result, 'timed_out': True}
                )
            else:
                return ToolResult(
                    text=f"Command failed with exit code {result['exit_code']}",
                    data=result
                )
    except ContainerError as e:
        return ToolResult(
            text=f"Container error: {str(e)}",
            data={'error': str(e), 'exit_code': e.exit_status}
        )
    except Exception as e:
        return ToolResult(
            text=f"Failed to execute command: {str(e)}",
            data={'error': str(e)}
        )


def execute_python_script(
    *,
    client: Any = None,
    container_name: str,
    script_content: str,
    script_args: str = "",
    timeout: int = 180,
    max_output_bytes: Optional[int] = None,
    packages: Optional[List[str]] = None
) -> ToolResult:
    """Execute a Python script inside a running container."""
    try:
        docker_client = client or DockerClient()
        
        # Install required packages first
        if packages:
            deps_result = add_dependencies(
                client=docker_client,
                container_name=container_name,
                dependencies=','.join(packages),
                language='python'
            )
            if "Failed" in deps_result.text:
                return ToolResult(
                    text=f"Failed to install required packages: {deps_result.text}",
                    data={'error': deps_result.data}
                )
        
        # Save script to container
        script_path = '/workspace/temp_script.py'
        docker_client.copy_to_container(
            container_name,
            script_path,
            script_content.encode('utf-8')
        )
        
        # Build command
        command = f"python {script_path}"
        if script_args:
            command += f" {script_args}"
        
        # Execute script
        result = execute_code(
            client=docker_client,
            container_name=container_name,
            command=command,
            timeout=timeout,
            max_output_bytes=max_output_bytes
        )
        
        # Clean up script file
        docker_client.execute_command(container_name, f"rm -f {script_path}")
        
        return result
    except Exception as e:
        return ToolResult(
            text=f"Failed to execute Python script: {str(e)}",
            data={'error': str(e)}
        )


def cleanup_container(
    *, 
    client: Any = None, 
    container_name: Optional[str] = None,
    session_id: Optional[str] = None,
    cleanup_all: bool = False,
    remove_volume: bool = False
) -> ToolResult:
    """Stop and remove a container; optionally remove its named volume."""
    try:
        docker_client = client or DockerClient()
        
        if cleanup_all:
            # Remove all MCP-managed containers
            removed = docker_client.cleanup_all_containers()
            return ToolResult(
                text=f"Removed {len(removed)} MCP-managed container(s)",
                data={'containers_removed': removed}
            )
        elif session_id:
            # Remove all containers for a session
            containers = docker_client.list_containers(
                all=True,
                filters={'label': f'mcp-session={session_id}'}
            )
            
            removed = []
            for container in containers:
                try:
                    docker_client.stop_container(container['id'])
                    docker_client.remove_container(container['id'])
                    removed.append(container['id'])
                except:
                    pass
            
            # Clean up session volumes if requested
            if remove_volume:
                docker_client.cleanup_session(session_id)
            
            return ToolResult(
                text=f"Removed {len(removed)} container(s) for session {session_id}",
                data={'containers_removed': removed, 'session': session_id}
            )
        elif container_name:
            # Remove specific container
            try:
                docker_client.stop_container(container_name)
                docker_client.remove_container(container_name)
                
                return ToolResult(
                    text=f"Successfully removed container {container_name}",
                    data={'container_removed': container_name}
                )
            except DockerException as e:
                return ToolResult(
                    text=f"Failed to remove container: {str(e)}",
                    data={'error': str(e)}
                )
        else:
            return ToolResult(
                text="No container specified for cleanup",
                data={'error': 'No container_name, session_id, or cleanup_all specified'}
            )
    except Exception as e:
        return ToolResult(
            text=f"Failed to cleanup: {str(e)}",
            data={'error': str(e)}
        )


def check_engine(*, client: Any = None) -> ToolResult:
    """Return engine info useful for diagnostics."""
    try:
        docker_client = client or DockerClient()
        engine_info = docker_client.check_engine()
        
        if engine_info['available']:
            return ToolResult(
                text=f"Docker engine is available (version {engine_info['version']})",
                data=engine_info
            )
        else:
            return ToolResult(
                text=f"Docker engine is not available: {engine_info.get('error', 'Unknown error')}",
                data=engine_info
            )
    except Exception as e:
        return ToolResult(
            text=f"Failed to check Docker engine: {str(e)}",
            data={'available': False, 'error': str(e)}
        )

