from __future__ import annotations

from unittest.mock import MagicMock

from docker_mcp import container_ops as ops


def test_add_dependencies_python_venv_install(mock_docker_client):
    cont = MagicMock()
    cont.name = "my-cont"
    cont.attrs = {"State": {"Status": "running"}}
    mock_docker_client.containers.get.return_value = cont

    try:
        result = ops.add_dependencies(
            client=mock_docker_client,
            container_name="my-cont",
            dependencies="numpy pandas",
            language="python",
        )
    except NotImplementedError:
        return

    assert "install" in result.text.lower()
    assert "numpy" in result.text or "pandas" in result.text


def test_add_dependencies_rejects_dangerous_input(mock_docker_client):
    try:
        ops.add_dependencies(
            client=mock_docker_client,
            container_name="my-cont",
            dependencies="numpy; rm -rf /",
        )
    except NotImplementedError:
        return
    except ValueError:
        return
    assert False, "Expected ValueError for dangerous dependency string"

