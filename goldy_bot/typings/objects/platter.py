from typing import Union, TypeVar

from ...objects.platter import Platter

__all__ = (
    "PlatterSelfT",
)

T = TypeVar("T")

PlatterSelfT = Union[Platter, T]