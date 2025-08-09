"""Docker client wrapper for container operations."""

import io
import json
import tarfile
import time
from typing import Dict, List, Optional, Any, Generator, Callable

import docker
from docker.errors import DockerException, APIError, ContainerError, ImageNotFound
from docker.models.containers import Container
from docker.types import LogConfig

from .config import config


class DockerClient:
    """Wrapper around Docker SDK for container operations."""
    
    def __init__(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
        except DockerException as e:
            raise DockerException(f"Failed to initialize Docker client: {str(e)}")
    
    def check_engine(self) -> Dict[str, Any]:
        """Check if Docker engine is available and get version info."""
        try:
            self.client.ping()
            version_info = self.client.version()
            return {
                'available': True,
                'version': version_info.get('Version', 'Unknown'),
                'api_version': version_info.get('ApiVersion', 'Unknown'),
                'os': version_info.get('Os', 'Unknown'),
                'arch': version_info.get('Arch', 'Unknown')
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def create_container(
        self,
        image: str,
        name: Optional[str] = None,
        command: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        network_enabled: bool = False,
        session_id: Optional[str] = None,
        persist_workspace: bool = False,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a new container with security restrictions."""
        # Prepare labels
        container_labels = {
            'mcp-managed': 'true',
            'mcp-session': session_id or ''
        }
        if labels:
            container_labels.update(labels)
        
        # Handle persistent workspace
        container_volumes = volumes or {}
        if persist_workspace and session_id:
            volume_name = f'mcp-session-{session_id}'
            # Create volume if it doesn't exist
            try:
                self.client.volumes.get(volume_name)
            except docker.errors.NotFound:
                self.client.volumes.create(
                    name=volume_name,
                    labels={'mcp-managed': 'true', 'mcp-session': session_id}
                )
            container_volumes[volume_name] = {'bind': '/workspace', 'mode': 'rw'}
        
        # Create container
        container = self.client.containers.create(
            image=image,
            name=name,
            command=command or '/bin/sh',
            detach=True,
            mem_limit=config.memory_limit,
            nano_cpus=int(config.cpu_limit * 1e9),
            pids_limit=config.pids_limit,
            network_mode='bridge' if network_enabled else 'none',
            security_opt=['no-new-privileges'],
            read_only=False,
            working_dir='/workspace',
            volumes=container_volumes,
            environment=environment or {},
            stdin_open=True,
            tty=True,
            labels=container_labels
        )
        
        return container.id
    
    def get_or_create_container(
        self,
        image: str,
        session_id: str,
        **kwargs
    ) -> str:
        """Get existing container for session or create new one."""
        # Check for existing container
        containers = self.list_containers(
            all=True,
            filters={'label': [f'mcp-managed=true', f'mcp-session={session_id}']}
        )
        
        if containers:
            container = containers[0]
            # Start container if it's stopped
            if container['status'] != 'running':
                self.start_container(container['id'])
            return container['id']
        
        # Create new container
        return self.create_container(
            image=image,
            session_id=session_id,
            persist_workspace=True,
            **kwargs
        )
    
    def start_container(self, container_id: str):
        """Start a container."""
        container = self.client.containers.get(container_id)
        container.start()
    
    def stop_container(self, container_id: str, timeout: int = 10):
        """Stop a container."""
        container = self.client.containers.get(container_id)
        container.stop(timeout=timeout)
    
    def remove_container(self, container_id: str):
        """Remove a container."""
        container = self.client.containers.get(container_id)
        container.remove(force=True)
    
    def _execute_command_stream(self, container, command: str, workdir: str):
        """Execute command with streaming output."""
        exec_result = container.exec_run(
            command,
            stdout=True,
            stderr=True,
            stream=True,
            demux=True,
            workdir=workdir
        )
        
        # exec_result is an ExecResult object with output generator
        for chunk in exec_result.output:
            if isinstance(chunk, tuple):
                stdout_chunk, stderr_chunk = chunk
                yield {
                    'stdout': stdout_chunk.decode('utf-8') if stdout_chunk else '',
                    'stderr': stderr_chunk.decode('utf-8') if stderr_chunk else ''
                }
            else:
                # Non-demuxed output
                yield {
                    'stdout': chunk.decode('utf-8') if chunk else '',
                    'stderr': ''
                }
    
    def execute_command(
        self,
        container_id: str,
        command: str,
        stream: bool = False,
        stdin: Optional[str] = None,
        workdir: str = '/workspace'
    ) -> Any:
        """Execute a command in a container."""
        container = self.client.containers.get(container_id)
        
        if stream:
            # Return the generator for streaming
            return self._execute_command_stream(container, command, workdir)
        else:
            # Non-streaming execution
            if stdin:
                # Handle interactive input
                exec_id = container.client.api.exec_create(
                    container.id,
                    command,
                    stdout=True,
                    stderr=True,
                    stdin=True,
                    workdir=workdir
                )['Id']
                
                socket = container.client.api.exec_start(
                    exec_id,
                    detach=False,
                    stream=True,
                    socket=True
                )
                
                # Send input
                socket._sock.send(stdin.encode('utf-8'))
                socket._sock.shutdown(1)  # Close write side
                
                # Read output
                output = b''
                while True:
                    chunk = socket._sock.recv(4096)
                    if not chunk:
                        break
                    output += chunk
                
                exec_info = container.client.api.exec_inspect(exec_id)
                return {
                    'exit_code': exec_info['ExitCode'],
                    'stdout': output.decode('utf-8'),
                    'stderr': ''
                }
            else:
                exec_result = container.exec_run(
                    command,
                    stdout=True,
                    stderr=True,
                    stream=False,
                    demux=True,
                    workdir=workdir
                )
                
                # Handle the output based on whether it's a tuple or not
                if isinstance(exec_result.output, tuple):
                    stdout, stderr = exec_result.output
                    # stderr can be None when demux=True
                    if stderr is None:
                        stderr = b''
                else:
                    stdout = exec_result.output
                    stderr = b''
                
                return {
                    'exit_code': exec_result.exit_code,
                    'stdout': stdout.decode('utf-8') if stdout else '',
                    'stderr': stderr.decode('utf-8') if stderr else ''
                }
    
    def list_containers(
        self,
        all: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List containers."""
        # Add MCP filter if using session filter
        if filters and 'label' in filters:
            if isinstance(filters['label'], str):
                filters = {'label': filters['label']}
            elif isinstance(filters['label'], list):
                filters = {'label': filters['label']}
        elif not filters:
            filters = {}
        
        containers = self.client.containers.list(all=all, filters=filters)
        
        result = []
        for container in containers:
            result.append({
                'id': container.id,
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'status': container.status,
                'created': container.attrs['Created'],
                'state': container.status,
                'labels': container.labels
            })
        
        return result
    
    def get_container_logs(
        self,
        container_id: str,
        tail: int = 100,
        timestamps: bool = False
    ) -> str:
        """Get container logs."""
        container = self.client.containers.get(container_id)
        logs = container.logs(
            stdout=True,
            stderr=True,
            tail=tail,
            timestamps=timestamps
        )
        return logs.decode('utf-8')
    
    def copy_to_container(
        self,
        container_id: str,
        path: str,
        data: bytes
    ):
        """Copy data to a file in the container."""
        container = self.client.containers.get(container_id)
        
        # Create tar archive in memory
        tar_stream = io.BytesIO()
        tar = tarfile.TarFile(fileobj=tar_stream, mode='w')
        
        # Add file to tar
        file_name = path.split('/')[-1]
        tarinfo = tarfile.TarInfo(name=file_name)
        tarinfo.size = len(data)
        tarinfo.mode = 0o644
        tar.addfile(tarinfo, io.BytesIO(data))
        tar.close()
        
        # Copy to container
        container.put_archive(
            path='/'.join(path.split('/')[:-1]) or '/workspace',
            data=tar_stream.getvalue()
        )
    
    def copy_from_container(
        self,
        container_id: str,
        path: str
    ) -> bytes:
        """Copy a file from the container."""
        container = self.client.containers.get(container_id)
        bits, _ = container.get_archive(path)
        
        # Extract from tar
        tar_stream = io.BytesIO()
        for chunk in bits:
            tar_stream.write(chunk)
        tar_stream.seek(0)
        
        tar = tarfile.TarFile(fileobj=tar_stream, mode='r')
        member = tar.getmembers()[0]
        return tar.extractfile(member).read()
    
    def pull_image(
        self,
        image: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        """Pull a Docker image."""
        if progress_callback:
            # Stream pull with progress
            for line in self.client.api.pull(image, stream=True):
                progress = json.loads(line)
                progress_callback(progress.get('status', ''))
        else:
            self.client.images.pull(image)
    
    def image_exists(self, image: str) -> bool:
        """Check if an image exists locally."""
        try:
            self.client.images.get(image)
            return True
        except ImageNotFound:
            return False
    
    def cleanup_all_containers(self) -> List[str]:
        """Remove all MCP-managed containers."""
        containers = self.client.containers.list(
            all=True,
            filters={'label': 'mcp-managed=true'}
        )
        
        removed = []
        for container in containers:
            try:
                container.stop(timeout=5)
            except:
                pass  # Container might already be stopped
            container.remove(force=True)
            removed.append(container.id)
        
        return removed
    
    def cleanup_session(self, session_id: str):
        """Clean up all resources for a session."""
        # Remove containers
        containers = self.client.containers.list(
            all=True,
            filters={'label': f'mcp-session={session_id}'}
        )
        
        for container in containers:
            try:
                container.stop(timeout=5)
            except:
                pass
            container.remove(force=True)
        
        # Remove volumes
        volumes = self.client.volumes.list(
            filters={'label': f'mcp-session={session_id}'}
        )
        
        for volume in volumes:
            volume.remove()
    
    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """Get container resource statistics."""
        container = self.client.containers.get(container_id)
        stats = container.stats(stream=False)
        
        # Calculate CPU percentage
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats['precpu_stats']['system_cpu_usage']
        cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0
        
        # Memory stats
        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']
        memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0
        
        return {
            'cpu_percent': cpu_percent,
            'memory_usage': memory_usage,
            'memory_limit': memory_limit,
            'memory_percent': memory_percent,
            'network_rx': sum(net['rx_bytes'] for net in stats.get('networks', {}).values()),
            'network_tx': sum(net['tx_bytes'] for net in stats.get('networks', {}).values())
        }
    
    def wait_for_ready(
        self,
        container_id: str,
        max_retries: int = 10,
        retry_delay: float = 0.5
    ) -> bool:
        """Wait for container to be ready."""
        container = self.client.containers.get(container_id)
        
        for _ in range(max_retries):
            # Check if container is running
            container.reload()
            if container.status != 'running':
                self.start_container(container_id)
                time.sleep(retry_delay)
                continue
            
            # Try a simple command to check if shell is responsive
            try:
                result = container.exec_run('echo ready', workdir='/workspace')
                if result.exit_code == 0:
                    return True
            except:
                pass
            
            time.sleep(retry_delay)
        
        return False
    
    def install_package(
        self,
        container_id: str,
        package: str,
        package_manager: str = 'pip'
    ) -> Dict[str, Any]:
        """Install a package in the container."""
        commands = {
            'pip': f'pip install {package}',
            'npm': f'npm install {package}',
            'apt': f'apt-get install -y {package}',
            'apk': f'apk add {package}'
        }
        
        if package_manager not in commands:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Unknown package manager: {package_manager}'
            }
        
        result = self.execute_command(
            container_id,
            commands[package_manager]
        )
        
        return {
            'success': result['exit_code'] == 0,
            'stdout': result['stdout'],
            'stderr': result['stderr']
        }
    
    def kill_process(
        self,
        container_id: str,
        process_pattern: str
    ) -> bool:
        """Kill a process in the container matching the pattern."""
        container = self.client.containers.get(container_id)
        
        # Find process
        result = container.exec_run(
            f"ps aux | grep '{process_pattern}' | grep -v grep",
            workdir='/workspace'
        )
        
        if result.exit_code != 0:
            return False
        
        # Extract PIDs
        lines = result.output.decode('utf-8').strip().split('\n')
        for line in lines:
            if line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    container.exec_run(f'kill {pid}')
        
        return True