from __future__ import annotations

import logging
from enum import Enum
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union, Callable, Any

if TYPE_CHECKING:
    from .. import Goldy
    from .platter import Platter
    from ..commands import Command
    from ..nextcore_utils.components.buttons.button import Button

INVOKABLE_TYPES = Union[Command, Button]

class InvokableType(Enum):
    PREFIX_CMD = 0
    SLASH_CMD = 1
    BUTTON = 2

# TODO: Make it a dict.
class Invokable(ABC, dict):
    """A hybrid abstract class that is inherited from every goldy bot object that can be invoked, like a command, a button or on-message event."""
    def __init__(
        self,
        name: str,
        data: dict,
        callback: Callable[[Platter], Any],
        goldy: Goldy,
        logger: logging.Logger
    ):
        self.__id: str = None
        self.__name = name

        self.callback = callback
        self.goldy = goldy
        self.logger = logger

        super().__init__(data)

    @property
    def id(self) -> str:
        """The id of the invokable. This is None when the invokable hasn't been invoked."""
        return self.__id

    @property
    def name(self) -> str:
        """The name of the invokable. This is used in log messages and more."""
        return self.__name

    def register(self, id: str) -> None:
        """Method to register this as invokable in goldy bot."""
        self.__id = id
        self.goldy.invokable_list.append((id, self))
        self.logger.debug(f"'{self.name}' has been registered!")

    @abstractmethod
    async def invoke(self, platter: Platter) -> Any:
        ...