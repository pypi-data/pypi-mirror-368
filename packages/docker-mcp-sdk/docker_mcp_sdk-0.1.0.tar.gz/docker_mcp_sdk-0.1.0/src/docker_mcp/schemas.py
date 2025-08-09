from __future__ import annotations

# JSON Schemas for MCP tool parameters and returns.

LIST_CONTAINERS_SCHEMA = {
    "type": "object",
    "properties": {
        "show_all": {"type": "boolean", "default": True},
    },
}

CREATE_CONTAINER_SCHEMA = {
    "type": "object",
    "required": ["image", "container_name"],
    "properties": {
        "image": {"type": "string", "minLength": 1},
        "container_name": {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9._-]+$",
            "minLength": 1,
        },
        "dependencies": {"type": "string", "default": ""},
        "network": {"type": "string", "enum": ["bridge", "none"], "default": "bridge"},
        "memory": {"type": "string"},
        "cpus": {"type": "number"},
        "pids_limit": {"type": "integer"},
    },
}

ADD_DEPENDENCIES_SCHEMA = {
    "type": "object",
    "required": ["container_name", "dependencies"],
    "properties": {
        "container_name": {"type": "string", "minLength": 1},
        "dependencies": {"type": "string", "minLength": 1},
        "language": {"type": "string", "enum": ["python", "node", "system"]},
        "package_manager": {"type": "string", "enum": ["pip", "npm", "apt", "apk"]},
    },
}

EXECUTE_CODE_SCHEMA = {
    "type": "object",
    "required": ["container_name", "command"],
    "properties": {
        "container_name": {"type": "string", "minLength": 1},
        "command": {"type": "string", "minLength": 1},
        "timeout": {"type": "integer", "minimum": 1, "maximum": 3600, "default": 120},
        "env": {"type": "object", "additionalProperties": {"type": "string"}},
        "max_output_bytes": {"type": "integer", "minimum": 1024},
    },
}

EXECUTE_PYTHON_SCRIPT_SCHEMA = {
    "type": "object",
    "required": ["container_name", "script_content"],
    "properties": {
        "container_name": {"type": "string", "minLength": 1},
        "script_content": {"type": "string", "minLength": 1},
        "script_args": {"type": "string", "default": ""},
        "timeout": {"type": "integer", "minimum": 1, "maximum": 3600, "default": 180},
        "max_output_bytes": {"type": "integer", "minimum": 1024},
    },
}

CLEANUP_CONTAINER_SCHEMA = {
    "type": "object",
    "required": ["container_name"],
    "properties": {
        "container_name": {"type": "string", "minLength": 1},
        "remove_volume": {"type": "boolean", "default": False},
    },
}

CHECK_ENGINE_SCHEMA = {
    "type": "object",
    "properties": {},
}

