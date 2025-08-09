"""Tests for Docker client wrapper."""

import pytest
from unittest.mock import MagicMock, patch, call
import docker
from docker.errors import DockerException, APIError, ContainerError, ImageNotFound
from docker_mcp.docker_client import DockerClient
from docker_mcp.config import config


class TestDockerClient:
    """Tests for DockerClient class."""
    
    @pytest.fixture
    def mock_docker_client(self):
        """Create a mock Docker client."""
        with patch('docker_mcp.docker_client.docker.from_env') as mock:
            yield mock
    
    @pytest.fixture
    def docker_client(self, mock_docker_client):
        """Create a DockerClient instance with mocked Docker SDK."""
        mock_client_instance = MagicMock()
        mock_docker_client.return_value = mock_client_instance
        client = DockerClient()
        return client
    
    def test_initialization(self, mock_docker_client):
        """Test DockerClient initialization."""
        mock_client_instance = MagicMock()
        mock_docker_client.return_value = mock_client_instance
        
        client = DockerClient()
        
        mock_docker_client.assert_called_once()
        assert client.client == mock_client_instance
    
    def test_initialization_failure(self, mock_docker_client):
        """Test DockerClient initialization when Docker is not available."""
        mock_docker_client.side_effect = DockerException("Docker not available")
        
        with pytest.raises(DockerException):
            DockerClient()
    
    def test_check_engine(self, docker_client):
        """Test checking Docker engine status."""
        docker_client.client.ping.return_value = True
        docker_client.client.version.return_value = {
            'Version': '24.0.7',
            'ApiVersion': '1.43',
            'Os': 'linux',
            'Arch': 'amd64'
        }
        
        result = docker_client.check_engine()
        
        assert result['available'] is True
        assert result['version'] == '24.0.7'
        assert result['api_version'] == '1.43'
        docker_client.client.ping.assert_called_once()
        docker_client.client.version.assert_called_once()
    
    def test_check_engine_unavailable(self, docker_client):
        """Test checking Docker engine when it's not available."""
        docker_client.client.ping.side_effect = DockerException("Cannot connect")
        
        result = docker_client.check_engine()
        
        assert result['available'] is False
        assert 'error' in result
        assert 'Cannot connect' in result['error']
    
    def test_create_container(self, docker_client):
        """Test creating a container with proper resource limits."""
        mock_container = MagicMock()
        mock_container.id = 'abc123'
        mock_container.name = 'test_container'
        mock_container.status = 'created'
        docker_client.client.containers.create.return_value = mock_container
        
        container_id = docker_client.create_container(
            image='python:3.11-slim',
            name='test_container'
        )
        
        assert container_id == 'abc123'
        docker_client.client.containers.create.assert_called_once_with(
            image='python:3.11-slim',
            name='test_container',
            detach=True,
            mem_limit=config.memory_limit,
            nano_cpus=int(config.cpu_limit * 1e9),
            pids_limit=config.pids_limit,
            network_mode='none',
            security_opt=['no-new-privileges'],
            read_only=False,
            working_dir='/workspace',
            volumes={},
            environment={},
            command='/bin/sh',
            stdin_open=True,
            tty=True,
            labels={'mcp-managed': 'true', 'mcp-session': ''}
        )
    
    def test_create_container_with_network(self, docker_client):
        """Test creating a container with network access."""
        mock_container = MagicMock()
        mock_container.id = 'abc123'
        docker_client.client.containers.create.return_value = mock_container
        
        container_id = docker_client.create_container(
            image='python:3.11-slim',
            name='test_container',
            network_enabled=True
        )
        
        assert container_id == 'abc123'
        create_call = docker_client.client.containers.create.call_args
        assert create_call.kwargs['network_mode'] == 'bridge'
    
    def test_create_container_with_session(self, docker_client):
        """Test creating a container with session persistence."""
        mock_container = MagicMock()
        mock_container.id = 'abc123'
        mock_volume = MagicMock()
        mock_volume.name = 'mcp-session-xyz123'
        docker_client.client.volumes.create.return_value = mock_volume
        docker_client.client.containers.create.return_value = mock_container
        
        container_id = docker_client.create_container(
            image='python:3.11-slim',
            name='test_container',
            session_id='xyz123',
            persist_workspace=True
        )
        
        assert container_id == 'abc123'
        docker_client.client.volumes.create.assert_called_once_with(
            name='mcp-session-xyz123',
            labels={'mcp-managed': 'true', 'mcp-session': 'xyz123'}
        )
        create_call = docker_client.client.containers.create.call_args
        assert 'mcp-session-xyz123:/workspace' in create_call.kwargs['volumes']
        assert create_call.kwargs['labels']['mcp-session'] == 'xyz123'
    
    def test_reuse_container(self, docker_client):
        """Test reusing an existing container for performance."""
        mock_container = MagicMock()
        mock_container.id = 'abc123'
        mock_container.status = 'running'
        docker_client.client.containers.list.return_value = [mock_container]
        
        container_id = docker_client.get_or_create_container(
            image='python:3.11-slim',
            session_id='xyz123'
        )
        
        assert container_id == 'abc123'
        docker_client.client.containers.list.assert_called_once_with(
            all=True,
            filters={'label': ['mcp-managed=true', 'mcp-session=xyz123']}
        )
        docker_client.client.containers.create.assert_not_called()
    
    def test_create_container_image_not_found(self, docker_client):
        """Test creating container with non-existent image."""
        docker_client.client.containers.create.side_effect = ImageNotFound("Image not found")
        
        with pytest.raises(ImageNotFound):
            docker_client.create_container(
                image='nonexistent:latest',
                name='test_container'
            )
    
    def test_start_container(self, docker_client):
        """Test starting a container."""
        mock_container = MagicMock()
        docker_client.client.containers.get.return_value = mock_container
        
        docker_client.start_container('abc123')
        
        docker_client.client.containers.get.assert_called_once_with('abc123')
        mock_container.start.assert_called_once()
    
    def test_stop_container(self, docker_client):
        """Test stopping a container."""
        mock_container = MagicMock()
        docker_client.client.containers.get.return_value = mock_container
        
        docker_client.stop_container('abc123', timeout=10)
        
        docker_client.client.containers.get.assert_called_once_with('abc123')
        mock_container.stop.assert_called_once_with(timeout=10)
    
    def test_remove_container(self, docker_client):
        """Test removing a container."""
        mock_container = MagicMock()
        docker_client.client.containers.get.return_value = mock_container
        
        docker_client.remove_container('abc123')
        
        docker_client.client.containers.get.assert_called_once_with('abc123')
        mock_container.remove.assert_called_once_with(force=True)
    
    def test_execute_command(self, docker_client):
        """Test executing a command in a container."""
        mock_container = MagicMock()
        mock_exec = MagicMock()
        mock_exec.output.return_value = (b'Hello, World!\n', b'')
        mock_container.exec_run.return_value = mock_exec
        docker_client.client.containers.get.return_value = mock_container
        
        result = docker_client.execute_command('abc123', 'echo "Hello, World!"')
        
        assert result['exit_code'] == 0
        assert result['stdout'] == 'Hello, World!\n'
        assert result['stderr'] == ''
        mock_container.exec_run.assert_called_once_with(
            'echo "Hello, World!"',
            stdout=True,
            stderr=True,
            stream=False,
            demux=True,
            workdir='/workspace'
        )
    
    def test_execute_command_with_stream(self, docker_client):
        """Test executing a command with streaming output."""
        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(
            output=[
                (b'Line 1\n', b''),
                (b'Line 2\n', b''),
                (b'', b'Error occurred\n')
            ],
            exit_code=1
        )
        docker_client.client.containers.get.return_value = mock_container
        
        results = []
        for chunk in docker_client.execute_command('abc123', 'test.sh', stream=True):
            results.append(chunk)
        
        assert len(results) == 3
        assert results[0] == {'stdout': 'Line 1\n', 'stderr': ''}
        assert results[1] == {'stdout': 'Line 2\n', 'stderr': ''}
        assert results[2] == {'stdout': '', 'stderr': 'Error occurred\n'}
        
        mock_container.exec_run.assert_called_once_with(
            'test.sh',
            stdout=True,
            stderr=True,
            stream=True,
            demux=True,
            workdir='/workspace'
        )
    
    def test_execute_command_with_input(self, docker_client):
        """Test executing a command with interactive input."""
        mock_container = MagicMock()
        mock_exec = MagicMock()
        mock_socket = MagicMock()
        mock_exec.output.return_value = (b'Enter name: Hello, Alice!\n', b'')
        mock_container.exec_run.return_value = mock_exec
        mock_container.api.exec_create.return_value = {'Id': 'exec123'}
        mock_container.api.exec_start.return_value = mock_socket
        docker_client.client.containers.get.return_value = mock_container
        
        result = docker_client.execute_command(
            'abc123',
            'python script.py',
            stdin='Alice\n'
        )
        
        assert 'Hello, Alice!' in result['stdout']
    
    def test_execute_command_timeout(self, docker_client):
        """Test command execution with timeout."""
        mock_container = MagicMock()
        mock_container.exec_run.side_effect = ContainerError(
            container='abc123',
            exit_status=124,
            command='sleep 100',
            image='python:3.11-slim',
            stderr=b'Command timed out'
        )
        docker_client.client.containers.get.return_value = mock_container
        
        with pytest.raises(ContainerError):
            docker_client.execute_command('abc123', 'sleep 100')
    
    def test_list_containers(self, docker_client):
        """Test listing containers."""
        mock_container1 = MagicMock()
        mock_container1.id = 'abc123'
        mock_container1.name = 'container1'
        mock_container1.status = 'running'
        mock_container1.image.tags = ['python:3.11-slim']
        mock_container1.attrs = {'Created': '2024-01-01T00:00:00Z'}
        
        mock_container2 = MagicMock()
        mock_container2.id = 'def456'
        mock_container2.name = 'container2'
        mock_container2.status = 'exited'
        mock_container2.image.tags = ['node:18-alpine']
        mock_container2.attrs = {'Created': '2024-01-02T00:00:00Z'}
        
        docker_client.client.containers.list.return_value = [mock_container1, mock_container2]
        
        containers = docker_client.list_containers(all=True)
        
        assert len(containers) == 2
        assert containers[0]['id'] == 'abc123'
        assert containers[0]['name'] == 'container1'
        assert containers[0]['status'] == 'running'
        assert containers[0]['image'] == 'python:3.11-slim'
        assert containers[1]['id'] == 'def456'
        assert containers[1]['name'] == 'container2'
        assert containers[1]['status'] == 'exited'
        
        docker_client.client.containers.list.assert_called_once_with(all=True)
    
    def test_list_containers_filtered(self, docker_client):
        """Test listing containers with filters."""
        mock_container = MagicMock()
        mock_container.id = 'abc123'
        mock_container.name = 'mcp_container'
        mock_container.status = 'running'
        mock_container.image.tags = ['python:3.11-slim']
        mock_container.attrs = {'Created': '2024-01-01T00:00:00Z'}
        
        docker_client.client.containers.list.return_value = [mock_container]
        
        containers = docker_client.list_containers(
            filters={'label': 'mcp-managed=true'}
        )
        
        assert len(containers) == 1
        assert containers[0]['name'] == 'mcp_container'
        
        docker_client.client.containers.list.assert_called_once_with(
            all=False,
            filters={'label': 'mcp-managed=true'}
        )
    
    def test_get_container_logs(self, docker_client):
        """Test getting container logs."""
        mock_container = MagicMock()
        mock_container.logs.return_value = b'Application started\nListening on port 8080\n'
        docker_client.client.containers.get.return_value = mock_container
        
        logs = docker_client.get_container_logs('abc123', tail=100)
        
        assert logs == 'Application started\nListening on port 8080\n'
        docker_client.client.containers.get.assert_called_once_with('abc123')
        mock_container.logs.assert_called_once_with(
            stdout=True,
            stderr=True,
            tail=100,
            timestamps=False
        )
    
    def test_get_container_logs_with_timestamps(self, docker_client):
        """Test getting container logs with timestamps."""
        mock_container = MagicMock()
        mock_container.logs.return_value = b'2024-01-01T00:00:00Z Application started\n'
        docker_client.client.containers.get.return_value = mock_container
        
        logs = docker_client.get_container_logs('abc123', timestamps=True)
        
        assert '2024-01-01T00:00:00Z Application started' in logs
        mock_container.logs.assert_called_once_with(
            stdout=True,
            stderr=True,
            tail=100,
            timestamps=True
        )
    
    def test_copy_to_container(self, docker_client):
        """Test copying files to a container."""
        mock_container = MagicMock()
        docker_client.client.containers.get.return_value = mock_container
        
        docker_client.copy_to_container('abc123', '/workspace/test.py', b'print("Hello")')
        
        docker_client.client.containers.get.assert_called_once_with('abc123')
        mock_container.put_archive.assert_called_once()
        
        # Verify the tar archive was created correctly
        call_args = mock_container.put_archive.call_args
        assert call_args[0][0] == '/workspace'
        assert call_args[0][1] is not None  # tar data
    
    def test_copy_from_container(self, docker_client):
        """Test copying files from a container."""
        mock_container = MagicMock()
        # Simulate tar archive data
        mock_container.get_archive.return_value = (b'file_content', {'name': 'test.py'})
        docker_client.client.containers.get.return_value = mock_container
        
        content = docker_client.copy_from_container('abc123', '/workspace/test.py')
        
        assert content == b'file_content'
        docker_client.client.containers.get.assert_called_once_with('abc123')
        mock_container.get_archive.assert_called_once_with('/workspace/test.py')
    
    def test_pull_image(self, docker_client):
        """Test pulling a Docker image."""
        mock_image = MagicMock()
        mock_image.tags = ['python:3.11-slim']
        docker_client.client.images.pull.return_value = mock_image
        
        docker_client.pull_image('python:3.11-slim')
        
        docker_client.client.images.pull.assert_called_once_with('python:3.11-slim')
    
    def test_pull_image_with_progress(self, docker_client):
        """Test pulling image with progress callback."""
        progress_updates = []
        
        def progress_callback(status):
            progress_updates.append(status)
        
        # Simulate streaming pull
        docker_client.client.api.pull.return_value = [
            '{"status": "Pulling from library/python"}',
            '{"status": "Downloading", "progress": "[=>    ] 1MB/10MB"}',
            '{"status": "Download complete"}'
        ]
        
        docker_client.pull_image('python:3.11-slim', progress_callback=progress_callback)
        
        assert len(progress_updates) > 0
    
    def test_image_exists(self, docker_client):
        """Test checking if an image exists."""
        mock_image = MagicMock()
        docker_client.client.images.get.return_value = mock_image
        
        exists = docker_client.image_exists('python:3.11-slim')
        
        assert exists is True
        docker_client.client.images.get.assert_called_once_with('python:3.11-slim')
    
    def test_image_not_exists(self, docker_client):
        """Test checking if an image doesn't exist."""
        docker_client.client.images.get.side_effect = ImageNotFound("Image not found")
        
        exists = docker_client.image_exists('nonexistent:latest')
        
        assert exists is False
    
    def test_cleanup_all_containers(self, docker_client):
        """Test cleaning up all MCP-managed containers."""
        mock_container1 = MagicMock()
        mock_container1.id = 'abc123'
        mock_container2 = MagicMock()
        mock_container2.id = 'def456'
        
        docker_client.client.containers.list.return_value = [mock_container1, mock_container2]
        
        removed = docker_client.cleanup_all_containers()
        
        assert removed == ['abc123', 'def456']
        mock_container1.stop.assert_called_once()
        mock_container1.remove.assert_called_once_with(force=True)
        mock_container2.stop.assert_called_once()
        mock_container2.remove.assert_called_once_with(force=True)
        docker_client.client.containers.list.assert_called_once_with(
            all=True,
            filters={'label': 'mcp-managed=true'}
        )
    
    def test_cleanup_session_resources(self, docker_client):
        """Test cleaning up session-specific resources."""
        mock_container = MagicMock()
        mock_container.id = 'abc123'
        mock_volume = MagicMock()
        mock_volume.name = 'mcp-session-xyz123'
        
        docker_client.client.containers.list.return_value = [mock_container]
        docker_client.client.volumes.list.return_value = [mock_volume]
        
        docker_client.cleanup_session('xyz123')
        
        mock_container.stop.assert_called_once()
        mock_container.remove.assert_called_once_with(force=True)
        mock_volume.remove.assert_called_once()
        
        docker_client.client.containers.list.assert_called_once_with(
            all=True,
            filters={'label': 'mcp-session=xyz123'}
        )
        docker_client.client.volumes.list.assert_called_once_with(
            filters={'label': 'mcp-session=xyz123'}
        )
    
    def test_get_container_stats(self, docker_client):
        """Test getting container statistics."""
        mock_container = MagicMock()
        mock_container.stats.return_value = {
            'cpu_stats': {'cpu_usage': {'total_usage': 1000000}},
            'memory_stats': {'usage': 52428800, 'limit': 1073741824},
            'networks': {'eth0': {'rx_bytes': 1024, 'tx_bytes': 2048}}
        }
        docker_client.client.containers.get.return_value = mock_container
        
        stats = docker_client.get_container_stats('abc123')
        
        assert 'cpu_percent' in stats
        assert 'memory_usage' in stats
        assert 'memory_limit' in stats
        assert 'memory_percent' in stats
        assert stats['memory_usage'] == 52428800
        assert stats['memory_limit'] == 1073741824
    
    def test_wait_for_container_ready(self, docker_client):
        """Test waiting for container to be ready."""
        mock_container = MagicMock()
        mock_container.status = 'running'
        mock_container.exec_run.side_effect = [
            MagicMock(exit_code=1),  # First check fails
            MagicMock(exit_code=1),  # Second check fails  
            MagicMock(exit_code=0),  # Third check succeeds
        ]
        docker_client.client.containers.get.return_value = mock_container
        
        ready = docker_client.wait_for_ready('abc123', max_retries=5)
        
        assert ready is True
        assert mock_container.exec_run.call_count == 3
    
    def test_install_package(self, docker_client):
        """Test installing packages in a container."""
        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(
            exit_code=0,
            output=(b'Successfully installed numpy-1.24.0\n', b'')
        )
        docker_client.client.containers.get.return_value = mock_container
        
        result = docker_client.install_package(
            'abc123',
            'numpy',
            package_manager='pip'
        )
        
        assert result['success'] is True
        assert 'numpy' in result['stdout']
        mock_container.exec_run.assert_called_once_with(
            'pip install numpy',
            stdout=True,
            stderr=True,
            stream=False,
            demux=True,
            workdir='/workspace'
        )
    
    def test_kill_process_in_container(self, docker_client):
        """Test killing a specific process in container."""
        mock_container = MagicMock()
        # First exec to find process
        mock_container.exec_run.side_effect = [
            MagicMock(exit_code=0, output=(b'1234 python script.py\n', b'')),
            MagicMock(exit_code=0, output=(b'', b''))
        ]
        docker_client.client.containers.get.return_value = mock_container
        
        killed = docker_client.kill_process('abc123', 'python script.py')
        
        assert killed is True
        assert mock_container.exec_run.call_count == 2
        # Second call should be kill command
        kill_call = mock_container.exec_run.call_args_list[1]
        assert 'kill' in kill_call[0][0]