from __future__ import annotations

from .cache import Cache
from .docker import Docker
from .legacy import Legacy
from .repositories import Repo
from .commands import Commands
from .extensions import Extensions

__all__ = (
    "FrameworkWrapper",
)

class FrameworkWrapper(Docker, Cache, Extensions, Legacy, Repo, Commands):
    def __init__(self) -> None:
        super().__init__()