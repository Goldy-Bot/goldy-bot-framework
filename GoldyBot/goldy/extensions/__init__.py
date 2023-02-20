from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, List

from ...goldy import get_goldy_instance
from ... import goldy_bot_logger, LoggerAdapter

extensions_cache:List[Tuple[str, object]] = [

]
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

        # Adding to cache and loading commands.
        # ---------------------------------------
        if not self.code_name in self.ignored_extensions_list:
            self.logger.debug("Adding to cache...")
            extensions_cache.append(
                (self.code_name, self)
            )
        
            self.logger.debug("Loading commands...")
            self.loader() # Load commands.

        else:
            self.logger.warn(
                "Not loading commands from this extension as it's ignored!"
            )

        # Cached commands list.
        self.__commands:List = [

        ]

        # TODO: Added command class to List type after command class is done.

    @property
    def code_name(self) -> str:
        return self.__class__.__name__

    def add_command(self, command) -> None:
        self.__commands.append(command)
        self.logger.debug(f"Added command {command}")
        return None
    
    def get_commands(self) -> List: # TODO: Also add the command class type here too.
        return self.__commands

    @abstractmethod
    def loader(self):
        """The extension's command loader. This is what Goldy Bot uses to load your commands in an extension."""
        ...