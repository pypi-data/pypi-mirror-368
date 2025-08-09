from __future__ import annotations

from docker_mcp import schemas


def test_list_containers_schema():
    s = schemas.LIST_CONTAINERS_SCHEMA
    assert s["type"] == "object"
    assert "show_all" in s["properties"]


def test_create_container_schema():
    s = schemas.CREATE_CONTAINER_SCHEMA
    assert set(s["required"]) == {"image", "container_name"}
    assert "dependencies" in s["properties"]
    assert s["properties"]["container_name"]["pattern"]


def test_add_dependencies_schema():
    s = schemas.ADD_DEPENDENCIES_SCHEMA
    assert set(s["required"]) == {"container_name", "dependencies"}
    assert "package_manager" in s["properties"]


def test_execute_code_schema():
    s = schemas.EXECUTE_CODE_SCHEMA
    assert set(s["required"]) == {"container_name", "command"}
    assert s["properties"]["timeout"]["maximum"] >= 3600


def test_execute_python_script_schema():
    s = schemas.EXECUTE_PYTHON_SCRIPT_SCHEMA
    assert set(s["required"]) == {"container_name", "script_content"}


def test_cleanup_container_schema():
    s = schemas.CLEANUP_CONTAINER_SCHEMA
    assert s["properties"]["remove_volume"]["default"] is False

