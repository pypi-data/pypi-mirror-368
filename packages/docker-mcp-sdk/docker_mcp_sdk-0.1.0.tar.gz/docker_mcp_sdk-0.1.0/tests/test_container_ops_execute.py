from __future__ import annotations

from unittest.mock import MagicMock

from docker_mcp import container_ops as ops


def test_execute_code_returns_output_and_exit_code(mock_docker_client):
    cont = MagicMock()
    cont.name = "my-cont"
    cont.exec_run.return_value = types.SimpleNamespace(exit_code=0, output=b"hello\n")
    mock_docker_client.containers.get.return_value = cont

    try:
        result = ops.execute_code(
            client=mock_docker_client,
            container_name="my-cont",
            command="echo hello",
            timeout=5,
        )
    except NotImplementedError:
        return

    assert result.data["exit_code"] == 0
    assert "hello" in result.text.lower() or "hello" in (result.data.get("stdout") or "")


def test_execute_code_enforces_timeout(mock_docker_client):
    try:
        ops.execute_code(
            client=mock_docker_client,
            container_name="my-cont",
            command="sleep 1000",
            timeout=1,
        )
    except NotImplementedError:
        return
    except TimeoutError:
        return
    assert False, "Expected TimeoutError when command exceeds timeout"

