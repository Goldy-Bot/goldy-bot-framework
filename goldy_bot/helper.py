from __future__ import annotations
from typing import Generic, TypeVar

__all__ = (
    "DictHelper",
)

T = TypeVar("T")

class DictHelper(Generic[T]): # TODO: Better name for this.
    def __init__(self, data: T, **kwargs) -> None:
        self.data = data

        self.data.update(kwargs)