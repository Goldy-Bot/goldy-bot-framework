from __future__ import annotations

from . import Application, User, Interaction

__all__ = (
    "DiscordWrapper",
)

class DiscordWrapper(Application, User, Interaction):
    def __init__(self) -> None:
        super().__init__()