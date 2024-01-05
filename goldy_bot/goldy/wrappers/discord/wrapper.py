from __future__ import annotations

from . import Application, User

__all__ = (
    "DiscordWrapper",
)

class DiscordWrapper(Application, User):
    def __init__(self) -> None:
        super().__init__()