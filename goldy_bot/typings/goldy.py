from typing import Union, TypeVar

from ..goldy import Goldy
from ..goldy.wrappers.low_level import LowLevelWrapper

__all__ = (
    "GoldySelfT",
    "LowLevelSelfT"
)

T = TypeVar("T")

GoldySelfT = Union[Goldy, T]
LowLevelSelfT = Union[LowLevelWrapper, T]