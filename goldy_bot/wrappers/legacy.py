from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from goldy_bot.goldy import Goldy

from GoldyBot.goldy.system import System

from .wrapper import Wrapper

__all__ = (
    "LegacyWrapper",
)

class LegacyWrapper(Wrapper):
    """Wraps some attributes from the legacy goldy class for the new 🥞 pancake one."""
    def __init__(self, goldy: Goldy) -> None:
        # self.__system = System(None)

        super().__init__(goldy)