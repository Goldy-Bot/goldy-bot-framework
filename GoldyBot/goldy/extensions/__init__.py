from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Tuple, List, TYPE_CHECKING

from ...goldy import get_goldy_instance
from ... import goldy_bot_logger, LoggerAdapter

if TYPE_CHECKING:
    from ..commands import Command

extensions_cache:List[Tuple[str, object]] = []
"""
This cache contains all the extensions that have been loaded and it's memory location to the class.
"""

class Extension(ABC):
    """
    The base class for a Goldy Bot extension.

    ---------------
    ### ***``Example:``***

    This is how you set up an extension in a GoldyBot module. 😍

    ```python
    class YourExtension(GoldyBot.Extension):
        def __init__(self):
            super().__init__()

        def loader(self):

            @GoldyBot.command()
            async def uwu(self:YourExtension, ctx):
                await send(ctx, f'Hi, {ctx.author.mention}! OwO!')

    def load():
        YourExtension()
    ```
    """

    def __init__(self):
        """Tells Goldy Bot to Load this class as an extension."""
        self.goldy = get_goldy_instance()
        self.ignored_extensions_list = self.goldy.config.ignored_extensions

        self.logger = LoggerAdapter(
            LoggerAdapter(goldy_bot_logger, prefix="Extensions"), 
            prefix=self.code_name
        )

        # Cached commands list.
        self.__commands:List[Command] = [

        ]

        self.__loaded_path = os.path.realpath(__file__)

        # Adding to cache and loading commands.
        # ---------------------------------------
        if not self.code_name in self.ignored_extensions_list:
            self.logger.debug("Adding myself to cache...")
            extensions_cache.append(
                (self.code_name, self)
            )
        
            self.logger.debug("Loading commands...")
            self.loader() # Load commands.

        else:
            self.logger.warn(
                "Not loading commands from this extension as it's ignored!"
            )

    @property
    def code_name(self) -> str:
        return self.__class__.__name__
    
    @property
    def loaded_path(self) -> str:
        "The path where this extension was loaded."
        return self.__loaded_path

    def add_command(self, command:Command) -> None:
        """Add this command to this extension."""
        self.__commands.append(command)
        self.logger.debug(f"Added the command '{command.name}' to {self.code_name}.")
        return None
    
    def get_commands(self) -> List[Command]:
        """Returns all the commands loaded with this extension."""
        return self.__commands
    
    def delete(self) -> None:
        """Unloads and deletes itself from cache and all the commands with it."""
        for command in self.get_commands():
            command.delete()

        extensions_cache.remove((self.code_name, self))

        self.logger.debug(f"Extension '{self.code_name}' removed!")

        return None

    @abstractmethod
    def loader(self):
        """The extension's command loader. This is what Goldy Bot uses to load your commands in an extension."""
        ...