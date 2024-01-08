from __future__ import annotations

from . import (
    Docker,
    Cache,
    Extensions,
    Legacy,
    Repo,
    Commands
)

__all__ = (
    "FrameworkWrapper",
)

class FrameworkWrapper(Docker, Cache, Extensions, Legacy, Repo, Commands):
    def __init__(self) -> None:
        super().__init__()