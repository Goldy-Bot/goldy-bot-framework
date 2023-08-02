from __future__ import annotations

from abc import ABC
from devgoldyutils import DictClass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..member import Member
    from ..invokable import Invokable

class Platter(ABC, DictClass):
    def __init__(self, data: dict, invoker: Member, invokable: Invokable) -> None:
        self.data = data
        """The raw data received right from discord that triggered this."""
        self.invoker = invoker
        """The member who triggered this platter."""
        self.invokable = invokable
        """The invokable object that was triggered. E.g. Command"""
        self.goldy = invokable.goldy
        """An instance of the goldy class."""
        self.logger = invokable.logger
        """A logger object you may use to log."""

        super().__init__(logger = invokable.logger)