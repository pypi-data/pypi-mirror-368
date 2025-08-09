# Docker MCP Server

A Model Context Protocol (MCP) server that enables LLMs to safely execute code in isolated Docker containers with strict resource limits and security controls.

## Features

- 🔒 **Secure Isolation**: Containers run with strict resource limits (memory, CPU, PIDs)
- 🏷️ **Session Management**: Group containers by session with persistent workspaces
- ♻️ **Container Reuse**: Optimize performance by reusing existing containers
- 📦 **Smart Dependencies**: Auto-detect and install packages (pip, npm, apt, apk)
- 🔄 **Streaming Output**: Real-time output for long-running processes
- 💾 **Persistent Workspaces**: Session-based volumes maintain state across executions

## Installation

```bash
# Clone the repository
git clone https://github.com/cevatkerim/docker-mcp.git
cd docker-mcp

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## Prerequisites

- Python 3.10+
- Docker Engine running locally
- MCP-compatible client (e.g., Claude Desktop)

## Quick Start

### 1. Start the MCP Server

```bash
python -m docker_mcp
```

### 2. Configure Your MCP Client

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "docker": {
      "command": "python",
      "args": ["-m", "docker_mcp"]
    }
  }
}
```

## Available Tools

### 1. check_engine
Check Docker engine availability and version.

```python
result = check_engine()
# Returns: Docker version and status
```

### 2. list_containers
List Docker containers with optional filtering.

```python
result = list_containers(
    show_all=True,  # Show all containers, not just running
    session_id="my-session"  # Filter by session
)
```

### 3. create_container
Create and start a new container with resource limits.

```python
result = create_container(
    image="python:3.11-slim",
    name="my-container",
    session_id="my-session",
    network_enabled=False,  # Network isolation by default
    reuse_existing=True,    # Reuse if exists
    environment={"KEY": "value"}
)
```

### 4. execute_code
Execute commands in a container.

```python
result = execute_code(
    container_id="my-container",
    command="echo 'Hello, World!'",
    timeout=30,
    stream=True,  # Stream output in real-time
    working_dir="/workspace"
)
```

### 5. execute_python_script
Execute Python scripts with automatic dependency management.

```python
result = execute_python_script(
    container_id="my-container",
    script="import numpy; print(numpy.__version__)",
    packages=["numpy"],  # Auto-install if needed
    timeout=60
)
```

### 6. add_dependencies
Install packages in a running container.

```python
result = add_dependencies(
    container_id="my-container",
    packages=["requests", "pandas"],
    package_manager="pip"  # Auto-detected if not specified
)
```

### 7. cleanup_container
Stop and remove containers with optional volume cleanup.

```python
# Remove specific container
result = cleanup_container(container_id="my-container")

# Remove all containers for a session
result = cleanup_container(session_id="my-session", remove_volumes=True)

# Remove all MCP-managed containers
result = cleanup_container(cleanup_all=True)
```

## Security Features

### Resource Limits
- **Memory**: 1GB default (configurable)
- **CPU**: 1.0 cores default (configurable)
- **Process IDs**: 512 max (configurable)
- **Network**: Isolated by default, opt-in for network access

### Container Labels
All containers are labeled with `mcp-managed=true` for easy identification and cleanup.

### Workspace Isolation
Each container gets a `/workspace` directory backed by a named volume, preventing host filesystem access.

## Configuration

Configure via environment variables:

```bash
export DOCKER_MCP_MEMORY_LIMIT=2147483648  # 2GB in bytes
export DOCKER_MCP_CPU_LIMIT=2.0            # 2 CPU cores
export DOCKER_MCP_PIDS_LIMIT=1024          # Max processes
export DOCKER_MCP_TIMEOUT=60               # Default timeout
export DOCKER_MCP_DEBUG=true               # Enable debug logging
```

## Examples

### Example 1: Python Data Analysis

```python
# Create a container for data analysis
container = create_container(
    image="python:3.11-slim",
    session_id="data-analysis"
)

# Install required packages
add_dependencies(
    container_id=container['container_id'],
    packages=["pandas", "matplotlib", "seaborn"]
)

# Execute analysis script
script = """
import pandas as pd
import matplotlib.pyplot as plt

# Create sample data
df = pd.DataFrame({
    'x': range(10),
    'y': [i**2 for i in range(10)]
})

# Save plot
df.plot(x='x', y='y')
plt.savefig('/workspace/plot.png')
print("Plot saved to /workspace/plot.png")
print(df.describe())
"""

execute_python_script(
    container_id=container['container_id'],
    script=script
)
```

### Example 2: Node.js Development

```python
# Create Node.js container
container = create_container(
    image="node:18-alpine",
    session_id="nodejs-dev",
    network_enabled=True  # Need network for npm
)

# Install packages
add_dependencies(
    container_id=container['container_id'],
    packages=["express", "axios"],
    package_manager="npm"
)

# Run Node.js code
execute_code(
    container_id=container['container_id'],
    command="node -e \"console.log('Node version:', process.version)\""
)
```

### Example 3: Multi-Language Project

```python
# Create container with Python and Node.js
container = create_container(
    image="nikolaik/python-nodejs:python3.11-nodejs18",
    session_id="multi-lang"
)

# Install Python packages
add_dependencies(
    container_id=container['container_id'],
    packages=["fastapi", "uvicorn"],
    package_manager="pip"
)

# Install Node packages
add_dependencies(
    container_id=container['container_id'],
    packages=["webpack", "babel-core"],
    package_manager="npm"
)
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term

# Run specific test file
pytest tests/test_docker_client.py -v
```

### Project Structure

```
docker-mcp/
├── src/
│   └── docker_mcp/
│       ├── __init__.py
│       ├── server.py         # MCP server implementation
│       ├── container_ops.py  # Tool implementations
│       ├── docker_client.py  # Docker SDK wrapper
│       ├── config.py         # Configuration
│       └── schemas.py        # Data models
├── tests/
│   ├── test_docker_client.py
│   ├── test_tools_comprehensive.py
│   └── ...
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Troubleshooting

### Docker Not Available
```
Error: Cannot connect to Docker daemon
```
**Solution**: Ensure Docker Desktop is running and the Docker socket is accessible.

### Permission Denied
```
Error: Permission denied while trying to connect to Docker daemon
```
**Solution**: Add your user to the docker group or run with appropriate permissions.

### Container Creation Failed
```
Error: Image not found
```
**Solution**: The image will be automatically pulled. Ensure you have internet connectivity.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Implement the feature
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.