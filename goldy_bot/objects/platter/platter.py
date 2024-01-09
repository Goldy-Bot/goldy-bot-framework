from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from goldy_bot.goldy import Goldy

    from discord_typings import InteractionData

from .wrappers import MessagingWrapper

__all__ = ("Platter",)

class Platter(MessagingWrapper):
    def __init__(self, data: InteractionData, goldy: Goldy) -> None:
        self.data = data
        self.goldy = goldy

        super().__init__(data, goldy)