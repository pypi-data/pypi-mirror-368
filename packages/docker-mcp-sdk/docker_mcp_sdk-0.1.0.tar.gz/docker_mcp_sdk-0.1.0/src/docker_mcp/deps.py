from __future__ import annotations

from typing import Iterable, Literal, Optional, Tuple

Language = Literal["python", "node", "system"]
PackageManager = Literal["pip", "npm", "apt", "apk"]


def detect_package_manager(*, which_exec) -> Tuple[Optional[Language], Optional[PackageManager]]:
    """Detect available language and package manager inside the container.

    `which_exec` is a callable that executes `which <bin>` and returns True/False.
    The real implementation will exec in the container; tests provide a stub.
    """
    raise NotImplementedError


def sanitize_dependencies(deps: str) -> Iterable[str]:
    """Split and validate dependency tokens, rejecting dangerous characters.

    Returns an iterable of safe package tokens. Raises ValueError on invalid input.
    """
    raise NotImplementedError


def install_dependencies(
    *,
    exec_run,
    workdir: str,
    deps: Iterable[str],
    language: Optional[Language],
    manager: Optional[PackageManager],
) -> str:
    """Install dependencies inside the container using detected manager.

    Returns a human-readable summary string.
    """
    raise NotImplementedError

