from __future__ import annotations

from . import Application, User, Interaction, Channel

__all__ = (
    "DiscordWrapper",
)

class DiscordWrapper(Application, User, Interaction, Channel):
    def __init__(self) -> None:
        super().__init__()