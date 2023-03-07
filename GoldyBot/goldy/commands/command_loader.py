from __future__ import annotations

from typing import List, overload, TYPE_CHECKING

from .. import Goldy
from ... import goldy_bot_logger, LoggerAdapter
from . import commands_cache

if TYPE_CHECKING:
    from . import Command

class CommandLoader():
    """Class that handles command loading."""
    def __init__(self, goldy:Goldy) -> None:
        self.goldy = goldy

        self.logger = LoggerAdapter(goldy_bot_logger, prefix="CommandLoader")

    @overload
    async def load(self) -> None:
        """Loads all commands that have been initialized in goldy bot."""
        ...

    @overload
    async def load(self, commands:List[Command]) -> None:
        """Loads each command in this list."""
        ...

    async def load(self, commands:List[Command] = None) -> None:
        """Loads all commands that have been initialized in goldy bot."""
        if commands is None:
            commands = [x[1] for x in commands_cache]

        for command in commands:
            if command.loaded is False:
                await command.load()
        
        return None