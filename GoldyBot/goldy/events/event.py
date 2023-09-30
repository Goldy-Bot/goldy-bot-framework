from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

from abc import ABC, abstractmethod

class Event(ABC): # TODO: We should probably inherit from invokable to slide events into the command invoke chain.
    """Base class that all Goldy Bot events inherit from."""
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def invoke(self):
        ...