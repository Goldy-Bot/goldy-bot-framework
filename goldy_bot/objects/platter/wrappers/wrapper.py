from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....goldy import Goldy

    from discord_typings import InteractionData

from abc import ABC

__all__ = (
    "PlatterWrapper",
)

class PlatterWrapper(ABC):
    def __init__(self, data: InteractionData, goldy: Goldy) -> None:
        self.data = data
        self.goldy = goldy
        super().__init__()