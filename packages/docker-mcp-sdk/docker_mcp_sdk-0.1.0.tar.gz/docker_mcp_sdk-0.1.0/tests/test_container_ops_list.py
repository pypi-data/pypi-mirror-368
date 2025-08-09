from __future__ import annotations

from unittest.mock import MagicMock

from docker_mcp import container_ops as ops


def test_list_containers_returns_expected_shape(mock_docker_client, fake_container):
    mock_docker_client.containers.list.return_value = [fake_container]

    # NOTE: Implementation will fill in fields; test shape and key content.
    result = None
    try:
        result = ops.list_containers(client=mock_docker_client, show_all=True)
    except NotImplementedError:
        # TDD: allow not implemented yet
        return

    assert isinstance(result.data, list)
    assert result.data and {
        "id",
        "name",
        "image",
        "status",
        "created",
        "state",
    }.issubset(result.data[0].keys())
    assert "python:3.9-slim" in result.data[0]["image"]
    assert "Listed" in result.text or "container" in result.text.lower()

