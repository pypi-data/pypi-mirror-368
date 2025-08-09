from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Configuration for Docker MCP server."""
    memory_limit: int = int(os.getenv("DOCKER_MCP_MEMORY_LIMIT", str(1024 * 1024 * 1024)))  # 1GB in bytes
    cpu_limit: float = float(os.getenv("DOCKER_MCP_CPU_LIMIT", "1.0"))
    pids_limit: int = int(os.getenv("DOCKER_MCP_PIDS_LIMIT", "512"))
    timeout: int = int(os.getenv("DOCKER_MCP_TIMEOUT", "30"))
    debug: bool = os.getenv("DOCKER_MCP_DEBUG", "false").lower() == "true"
    default_network: str = os.getenv("DOCKER_MCP_DEFAULT_NETWORK", "none")
    max_output_bytes: int = int(os.getenv("DOCKER_MCP_MAX_OUTPUT_BYTES", "200000"))


config = Config()
DEFAULTS = config  # For backward compatibility

