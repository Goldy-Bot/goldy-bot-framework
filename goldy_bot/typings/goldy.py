from typing import Union
from typing_extensions import Self

from ..goldy import Goldy

__all__ = (
    "GoldySelfT",
)

GoldySelfT = Union[Goldy, Self]