from typing import Union, TypeVar

from ..goldy import Goldy

__all__ = (
    "GoldySelfT",
)

T = TypeVar("T")

GoldySelfT = Union[Goldy, T]