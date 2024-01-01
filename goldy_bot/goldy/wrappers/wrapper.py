from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..goldy import Goldy

from abc import ABC

__all__ = (
    "Wrapper",
)

class Wrapper(ABC):
    def __init__(self, goldy: Goldy) -> None:
        super().__init__()