"""Comprehensive tests for all MCP tools."""

import pytest
from unittest.mock import MagicMock, patch, call, PropertyMock
import json
from datetime import datetime
from docker.errors import DockerException, APIError, ContainerError, ImageNotFound

from docker_mcp.container_ops import (
    check_engine,
    list_containers,
    create_container,
    execute_code,
    execute_python_script,
    add_dependencies,
    cleanup_container,
    ToolResult
)


class TestCheckEngineTool:
    """Tests for check_engine tool."""
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_check_engine_success(self, mock_docker_class):
        """Test successful Docker engine check."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.check_engine.return_value = {
            'available': True,
            'version': '24.0.7',
            'api_version': '1.43',
            'os': 'linux',
            'arch': 'amd64'
        }
        
        result = check_engine()
        
        assert isinstance(result, ToolResult)
        assert result.data["available"] is True
        assert result.data["version"] == '24.0.7'
        assert 'Docker engine is available' in result.text
        mock_client.check_engine.assert_called_once()
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_check_engine_unavailable(self, mock_docker_class):
        """Test Docker engine unavailable."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.check_engine.return_value = {
            'available': False,
            'error': 'Cannot connect to Docker daemon'
        }
        
        result = check_engine()
        
        assert isinstance(result, ToolResult)
        assert result.data["available"] is False
        assert result.data["error"] == 'Cannot connect to Docker daemon'
        assert 'not available' in result.text
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_check_engine_initialization_error(self, mock_docker_class):
        """Test Docker client initialization error."""
        mock_docker_class.side_effect = DockerException("Failed to initialize")
        
        result = check_engine()
        
        assert isinstance(result, ToolResult)
        assert result.data["available"] is False
        assert 'Failed to initialize' in result.data["error"]


class TestListContainersTool:
    """Tests for list_containers tool."""
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_list_containers_empty(self, mock_docker_class):
        """Test listing containers when none exist."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.list_containers.return_value = []
        
        result = list_containers()
        
        assert isinstance(result, ToolResult)
        assert result.data == []
        assert 'No containers' in result.text
        mock_client.list_containers.assert_called_once_with(all=False)
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_list_containers_with_data(self, mock_docker_class):
        """Test listing containers with multiple containers."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.list_containers.return_value = [
            {
                'id': 'abc123',
                'name': 'mcp-python-1',
                'image': 'python:3.11-slim',
                'status': 'running',
                'created': '2024-01-01T00:00:00Z',
                'state': 'running',
                'labels': {'mcp-session': 'session1'}
            },
            {
                'id': 'def456',
                'name': 'mcp-node-1',
                'image': 'node:18-alpine',
                'status': 'exited',
                'created': '2024-01-02T00:00:00Z',
                'state': 'exited',
                'labels': {'mcp-session': 'session2'}
            }
        ]
        
        result = list_containers(show_all=True)
        
        assert isinstance(result, ToolResult)
        assert len(result.data) == 2
        assert result.data[0]['id'] == 'abc123'
        assert result.data[0]['name'] == 'mcp-python-1'
        assert result.data[1]['status'] == 'exited'
        assert 'Listed 2 containers' in result.text
        mock_client.list_containers.assert_called_once_with(all=True)
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_list_containers_with_session_filter(self, mock_docker_class):
        """Test listing containers filtered by session."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.list_containers.return_value = [
            {
                'id': 'abc123',
                'name': 'mcp-python-session1',
                'image': 'python:3.11-slim',
                'status': 'running',
                'created': '2024-01-01T00:00:00Z',
                'state': 'running',
                'labels': {'mcp-session': 'session1'}
            }
        ]
        
        result = list_containers(session_id='session1')
        
        assert isinstance(result, ToolResult)
        assert len(result.data) == 1
        assert result.data[0]['labels']['mcp-session'] == 'session1'
        mock_client.list_containers.assert_called_once_with(
            all=False,
            filters={'label': 'mcp-session=session1'}
        )
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_list_containers_error_handling(self, mock_docker_class):
        """Test error handling in list_containers."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.list_containers.side_effect = DockerException("API error")
        
        with pytest.raises(DockerException):
            list_containers()


class TestCreateContainerTool:
    """Tests for create_container tool."""
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_create_container_basic(self, mock_docker_class):
        """Test creating a basic container."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.create_container.return_value = 'abc123'
        mock_client.start_container.return_value = None
        mock_client.wait_for_ready.return_value = True
        
        result = create_container(image='python:3.11-slim')
        
        assert isinstance(result, ToolResult)
        assert result.data["container_id"] == 'abc123'
        assert result.data.get("success", True) is True
        assert 'Container created' in result.text
        mock_client.create_container.assert_called_once()
        mock_client.start_container.assert_called_once_with('abc123')
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_create_container_with_session(self, mock_docker_class):
        """Test creating a container with session persistence."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.get_or_create_container.return_value = 'existing123'
        
        result = create_container(
            image='python:3.11-slim',
            session_id='test-session',
            reuse_existing=True
        )
        
        assert isinstance(result, ToolResult)
        assert result.data["container_id"] == 'existing123'
        assert result.data["reused"] is True
        mock_client.get_or_create_container.assert_called_once_with(
            image='python:3.11-slim',
            session_id='test-session'
        )
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_create_container_with_environment(self, mock_docker_class):
        """Test creating a container with environment variables."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.create_container.return_value = 'abc123'
        mock_client.start_container.return_value = None
        mock_client.wait_for_ready.return_value = True
        
        result = create_container(
            image='python:3.11-slim',
            environment={'API_KEY': 'secret', 'DEBUG': 'true'}
        )
        
        assert result.data["container_id"] == 'abc123'
        create_call = mock_client.create_container.call_args
        assert create_call.kwargs['environment'] == {'API_KEY': 'secret', 'DEBUG': 'true'}
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_create_container_with_network(self, mock_docker_class):
        """Test creating a container with network access."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.create_container.return_value = 'abc123'
        mock_client.start_container.return_value = None
        mock_client.wait_for_ready.return_value = True
        
        result = create_container(
            image='python:3.11-slim',
            network_enabled=True
        )
        
        assert result.data["container_id"] == 'abc123'
        create_call = mock_client.create_container.call_args
        assert create_call.kwargs['network_enabled'] is True
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_create_container_image_pull(self, mock_docker_class):
        """Test container creation with automatic image pull."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.image_exists.return_value = False
        mock_client.pull_image.return_value = None
        mock_client.create_container.return_value = 'abc123'
        mock_client.start_container.return_value = None
        mock_client.wait_for_ready.return_value = True
        
        result = create_container(image='python:3.11-slim')
        
        assert result.data["container_id"] == 'abc123'
        mock_client.image_exists.assert_called_once_with('python:3.11-slim')
        mock_client.pull_image.assert_called_once_with('python:3.11-slim')
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_create_container_failure(self, mock_docker_class):
        """Test container creation failure."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.create_container.side_effect = DockerException("Creation failed")
        
        result = create_container(image='python:3.11-slim')
        
        assert result.data.get("success", True) is False
        assert 'Creation failed' in result.data["error"]
        assert result.data["container_id"] is None


class TestExecuteCodeTool:
    """Tests for execute_code tool."""
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_code_success(self, mock_docker_class):
        """Test successful code execution."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.execute_command.return_value = {
            'exit_code': 0,
            'stdout': 'Hello, World!\n',
            'stderr': ''
        }
        
        result = execute_code(
            container_name='abc123',
            command='echo "Hello, World!"'
        )
        
        assert isinstance(result, ToolResult)
        assert result.data["exit_code"] == 0
        assert result.data["stdout"] == 'Hello, World!\n'
        assert result.data["stderr"] == ''
        assert 'executed successfully' in result.text
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_code_with_error(self, mock_docker_class):
        """Test code execution with error output."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.execute_command.return_value = {
            'exit_code': 1,
            'stdout': '',
            'stderr': 'Command not found\n'
        }
        
        result = execute_code(
            container_name='abc123',
            command='nonexistent_command'
        )
        
        assert result.data["exit_code"] == 1
        assert result.data["stderr"] == 'Command not found\n'
        assert 'failed with exit code 1' in result.text
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_code_streaming(self, mock_docker_class):
        """Test streaming code execution."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        
        # Simulate streaming output
        def stream_generator():
            yield {'stdout': 'Line 1\n', 'stderr': ''}
            yield {'stdout': 'Line 2\n', 'stderr': ''}
            yield {'stdout': 'Line 3\n', 'stderr': ''}
        
        mock_client.execute_command.return_value = stream_generator()
        
        result = execute_code(
            container_name='abc123',
            command='for i in 1 2 3; do echo "Line $i"; done',
            stream=True
        )
        
        # Collect streaming results
        output_lines = []
        for chunk in result:
            if chunk.get('stdout'):
                output_lines.append(chunk['stdout'])
        
        assert len(output_lines) == 3
        assert 'Line 1\n' in output_lines
        assert 'Line 3\n' in output_lines
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_code_with_timeout(self, mock_docker_class):
        """Test code execution with timeout."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.execute_command.side_effect = ContainerError(
            container='abc123',
            exit_status=124,
            command='sleep 100',
            image='python',
            stderr=b'Timeout'
        )
        
        result = execute_code(
            container_name='abc123',
            command='sleep 100',
            timeout=5
        )
        
        assert result.data["exit_code"] == 124
        assert result.data["timed_out"] is True
        assert 'timed out' in result.text
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_code_with_working_dir(self, mock_docker_class):
        """Test code execution with custom working directory."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.execute_command.return_value = {
            'exit_code': 0,
            'stdout': '/app\n',
            'stderr': ''
        }
        
        result = execute_code(
            container_name='abc123',
            command='pwd',
            working_dir='/app'
        )
        
        assert result.data["stdout"] == '/app\n'
        execute_call = mock_client.execute_command.call_args
        assert execute_call.kwargs.get('workdir') == '/app'


class TestExecutePythonScriptTool:
    """Tests for execute_python_script tool."""
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_python_script_simple(self, mock_docker_class):
        """Test executing a simple Python script."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        
        # Mock file copy and execution
        mock_client.copy_to_container.return_value = None
        mock_client.execute_command.return_value = {
            'exit_code': 0,
            'stdout': 'Hello from Python!\n42\n',
            'stderr': ''
        }
        
        script = '''
print("Hello from Python!")
result = 40 + 2
print(result)
'''
        
        result = execute_python_script(
            container_name='abc123',
            script_content=script
        )
        
        assert isinstance(result, ToolResult)
        assert result.data["exit_code"] == 0
        assert 'Hello from Python!' in result.data["stdout"]
        assert '42' in result.data["stdout"]
        mock_client.copy_to_container.assert_called_once()
        mock_client.execute_command.assert_called_once()
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_python_script_with_packages(self, mock_docker_class):
        """Test executing Python script that uses packages."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        
        mock_client.copy_to_container.return_value = None
        mock_client.execute_command.return_value = {
            'exit_code': 0,
            'stdout': '[[1, 2], [3, 4]]\n',
            'stderr': ''
        }
        
        script = '''
import numpy as np
arr = np.array([[1, 2], [3, 4]])
print(arr.tolist())
'''
        
        result = execute_python_script(
            container_name='abc123',
            script=script,
            packages=['numpy']
        )
        
        assert result.data["exit_code"] == 0
        assert '[[1, 2], [3, 4]]' in result.data["stdout"]
        # Should install packages first
        assert mock_client.execute_command.call_count >= 1
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_python_script_with_error(self, mock_docker_class):
        """Test Python script execution with runtime error."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        
        mock_client.copy_to_container.return_value = None
        mock_client.execute_command.return_value = {
            'exit_code': 1,
            'stdout': '',
            'stderr': 'Traceback (most recent call last):\n  File "script.py", line 1\nNameError: name "undefined_var" is not defined\n'
        }
        
        script = 'print(undefined_var)'
        
        result = execute_python_script(
            container_name='abc123',
            script_content=script
        )
        
        assert result.data["exit_code"] == 1
        assert 'NameError' in result.data["stderr"]
        assert 'undefined_var' in result.data["stderr"]
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_execute_python_script_with_args(self, mock_docker_class):
        """Test Python script execution with command line arguments."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        
        mock_client.copy_to_container.return_value = None
        mock_client.execute_command.return_value = {
            'exit_code': 0,
            'stdout': 'Arguments: arg1 arg2 arg3\n',
            'stderr': ''
        }
        
        script = '''
import sys
print(f"Arguments: {' '.join(sys.argv[1:])}")
'''
        
        result = execute_python_script(
            container_name='abc123',
            script=script,
            args=['arg1', 'arg2', 'arg3']
        )
        
        assert result.data["exit_code"] == 0
        assert 'arg1 arg2 arg3' in result.data["stdout"]


class TestAddDependenciesTool:
    """Tests for add_dependencies tool."""
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_add_pip_dependencies(self, mock_docker_class):
        """Test adding Python packages via pip."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.install_package.return_value = {
            'success': True,
            'stdout': 'Successfully installed numpy-1.24.0 pandas-2.0.0\n',
            'stderr': ''
        }
        
        result = add_dependencies(
            container_name='abc123',
            dependencies='numpy,pandas',
            package_manager='pip'
        )
        
        assert isinstance(result, ToolResult)
        assert result.data.get("success", True) is True
        assert 'numpy' in result.text
        assert 'pandas' in result.text
        # Should call install_package for each package
        assert mock_client.install_package.call_count == 2
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_add_npm_dependencies(self, mock_docker_class):
        """Test adding Node.js packages via npm."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.install_package.return_value = {
            'success': True,
            'stdout': 'added 50 packages\n',
            'stderr': ''
        }
        
        result = add_dependencies(
            container_name='abc123',
            dependencies='express,axios',
            package_manager='npm'
        )
        
        assert result.data.get("success", True) is True
        assert 'Installed 2 packages' in result.text
        calls = mock_client.install_package.call_args_list
        assert any('express' in str(call) for call in calls)
        assert any('axios' in str(call) for call in calls)
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_add_apt_dependencies(self, mock_docker_class):
        """Test adding system packages via apt."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        
        # First update apt
        mock_client.execute_command.return_value = {
            'exit_code': 0,
            'stdout': 'Reading package lists... Done\n',
            'stderr': ''
        }
        
        mock_client.install_package.return_value = {
            'success': True,
            'stdout': 'Setting up curl...\n',
            'stderr': ''
        }
        
        result = add_dependencies(
            container_name='abc123',
            dependencies='curl,git',
            package_manager='apt'
        )
        
        assert result.data.get("success", True) is True
        # Should update apt first
        mock_client.execute_command.assert_called_once_with(
            'abc123',
            'apt-get update'
        )
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_add_dependencies_failure(self, mock_docker_class):
        """Test handling package installation failure."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.install_package.side_effect = [
            {'success': True, 'stdout': 'Installed numpy\n', 'stderr': ''},
            {'success': False, 'stdout': '', 'stderr': 'ERROR: Could not find package invalid-package'}
        ]
        
        result = add_dependencies(
            container_name='abc123',
            dependencies='numpy,invalid-package',
            package_manager='pip'
        )
        
        assert result.data.get("success", True) is False
        assert 'Failed to install some packages' in result.text
        assert len(result.data["failed_packages"]) == 1
        assert 'invalid-package' in result.data["failed_packages"]
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_add_dependencies_requirements_file(self, mock_docker_class):
        """Test installing from requirements file."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        
        requirements = "numpy==1.24.0\npandas>=2.0.0\nscipy"
        
        mock_client.copy_to_container.return_value = None
        mock_client.execute_command.return_value = {
            'exit_code': 0,
            'stdout': 'Successfully installed all packages\n',
            'stderr': ''
        }
        
        result = add_dependencies(
            container_name='abc123',
            requirements_file=requirements,
            package_manager='pip'
        )
        
        assert result.data.get("success", True) is True
        mock_client.copy_to_container.assert_called_once()
        execute_call = mock_client.execute_command.call_args
        assert 'pip install -r' in execute_call[0][1]


class TestCleanupContainerTool:
    """Tests for cleanup_container tool."""
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_cleanup_single_container(self, mock_docker_class):
        """Test cleaning up a single container."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.stop_container.return_value = None
        mock_client.remove_container.return_value = None
        
        result = cleanup_container(container_name='abc123')
        
        assert isinstance(result, ToolResult)
        assert result.data.get("success", True) is True
        assert result.data["containers_removed"] == ['abc123']
        assert 'Removed container abc123' in result.text
        mock_client.stop_container.assert_called_once_with('abc123', timeout=10)
        mock_client.remove_container.assert_called_once_with('abc123')
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_cleanup_session_containers(self, mock_docker_class):
        """Test cleaning up all containers in a session."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.cleanup_session.return_value = None
        mock_client.list_containers.return_value = [
            {'id': 'abc123', 'name': 'session1-1'},
            {'id': 'def456', 'name': 'session1-2'}
        ]
        
        result = cleanup_container(session_id='session1')
        
        assert result.data.get("success", True) is True
        assert len(result.data["containers_removed"]) == 2
        assert 'abc123' in result.data["containers_removed"]
        assert 'def456' in result.data["containers_removed"]
        mock_client.cleanup_session.assert_called_once_with('session1')
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_cleanup_all_containers(self, mock_docker_class):
        """Test cleaning up all MCP-managed containers."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.cleanup_all_containers.return_value = ['abc123', 'def456', 'ghi789']
        
        result = cleanup_container(cleanup_all=True)
        
        assert result.data.get("success", True) is True
        assert len(result.data["containers_removed"]) == 3
        assert 'Removed 3 containers' in result.text
        mock_client.cleanup_all_containers.assert_called_once()
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_cleanup_container_not_found(self, mock_docker_class):
        """Test cleanup when container doesn't exist."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.stop_container.side_effect = DockerException("No such container")
        
        result = cleanup_container(container_name='nonexistent')
        
        assert result.data.get("success", True) is False
        assert 'No such container' in result.data["error"]
        assert result.data["containers_removed"] == []
    
    @patch('docker_mcp.container_ops.DockerClient')
    def test_cleanup_with_volumes(self, mock_docker_class):
        """Test cleanup including associated volumes."""
        mock_client = MagicMock()
        mock_docker_class.return_value = mock_client
        mock_client.stop_container.return_value = None
        mock_client.remove_container.return_value = None
        mock_client.cleanup_session.return_value = None
        
        result = cleanup_container(
            container_name='abc123',
            remove_volume=True
        )
        
        assert result.data.get("success", True) is True
        assert result.data.get("volumes_removed") is not None
        # Verify volume cleanup was attempted