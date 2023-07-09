from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union, Callable, Any

if TYPE_CHECKING:
    from .. import Goldy
    from .platter import Platter
    from ..recipes import Recipe
    from ..commands.command import Command

    INVOKABLE_TYPES = Union[Command, Recipe]

class Invokable(ABC, dict):
    """A hybrid abstract class that is inherited from every goldy bot object that can be invoked from discord, like a command, a button or on-message event."""
    def __init__(
        self,
        name: str,
        data: dict,
        callback: Callable[[Platter], Any],
        goldy: Goldy,
        logger: logging.Logger,
        pre_register: bool = True
    ):
        self.__id: str = None
        self.__name = name

        self.callback = callback
        self.goldy = goldy
        self.logger = logger

        # Preregistering invokables.
        if pre_register:
            self.goldy.pre_invokables.add(self)
            self.logger.debug("Invokable has been PRE-registered.")

        super().__init__(data)

    # Little trick to make all invokables hashable for set classes.
    def __hash__(self): return id(self)

    @property
    def id(self) -> str | None:
        """The id of the invokable. This is None when the invokable hasn't been registered."""
        return self.__id

    @property
    def name(self) -> str:
        """The name of the invokable. This is used in log messages and more."""
        return self.__name

    def register(self, id: str) -> None:
        """Method to register this as an invokable."""
        self.__id = id
        self.goldy.invokables.add((id, self))

        if self in self.goldy.pre_invokables:
            self.goldy.pre_invokables.remove(self)

        self.logger.debug(f"'{self.name}' has been registered with id '{id}'!")

    def unregister(self) -> None:
        """Deletes and removes this invokable from the registration list, making it no longer invokable."""
        self.goldy.invokables.remove(
            (self.id, self)
        )

        self.logger.debug(
            f"Invokable '{self.name}' has been unregistered!"
        )

        return None

    @abstractmethod
    async def invoke(self, platter: Platter) -> Any:
        ...