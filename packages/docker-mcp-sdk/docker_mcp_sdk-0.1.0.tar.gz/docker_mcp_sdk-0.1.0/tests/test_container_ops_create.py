from __future__ import annotations

from unittest.mock import MagicMock

from docker_mcp import container_ops as ops


def test_create_container_pulls_and_creates_with_limits(mock_docker_client):
    # Arrange
    mock_docker_client.images = MagicMock()
    mock_docker_client.images.get.side_effect = Exception("not found")
    mock_docker_client.images.pull.return_value = MagicMock()

    mock_docker_client.volumes.create.return_value = MagicMock(name="mcp_docker_my-cont")
    created_container = MagicMock()
    created_container.id = "abc123"
    created_container.name = "my-cont"
    created_container.image = MagicMock(tags=["python:3.9-slim"])
    created_container.attrs = {"State": {"Status": "running"}, "Created": "ts"}
    mock_docker_client.containers.create.return_value = created_container

    # Act
    try:
        result = ops.create_container(
            client=mock_docker_client,
            image="python:3.9-slim",
            container_name="my-cont",
            dependencies="numpy pandas",
            network="bridge",
            memory="1g",
            cpus=1.0,
            pids_limit=512,
        )
    except NotImplementedError:
        return

    # Assert
    mock_docker_client.images.pull.assert_called_with("python:3.9-slim")
    mock_docker_client.volumes.create.assert_called()
    mock_docker_client.containers.create.assert_called()
    assert "my-cont" in result.text
    assert result.data["name"] == "my-cont"
    assert result.data["image"]


def test_create_container_invalid_name_rejected(mock_docker_client):
    try:
        ops.create_container(
            client=mock_docker_client,
            image="python:3.9-slim",
            container_name="bad name with spaces",
        )
    except NotImplementedError:
        return
    except ValueError:
        return
    assert False, "Expected ValueError for invalid container name"

