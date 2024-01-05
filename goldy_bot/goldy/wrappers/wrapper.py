from __future__ import annotations

from . import (
    Docker,
    Cache,
    Extensions,
    Legacy,
    Repo
)

__all__ = (
    "FrameworkWrapper",
)

class FrameworkWrapper(Docker, Cache, Extensions, Legacy, Repo):
    def __init__(self) -> None:
        super().__init__()