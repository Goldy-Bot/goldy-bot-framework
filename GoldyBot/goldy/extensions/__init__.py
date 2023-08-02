from __future__ import annotations

import os
from devgoldyutils import Colours
from typing import Tuple, List, TYPE_CHECKING

from ...goldy import get_goldy_instance
from ... import goldy_bot_logger, LoggerAdapter

if TYPE_CHECKING:
    from ... import Goldy
    from ..commands.command import Command
    from .extension_metadata import ExtensionMetadata

extensions_cache: List[Tuple[str, object]] = []
"""
This cache contains all the extensions that have been loaded and it's memory location to the class.
"""

class Extension():
    """
    The base class for a Goldy Bot extension. 

    ---------------

    ⭐ Example:
    -------------
    This is how you set up an extension in a GoldyBot module::
    
        class YourExtension(GoldyBot.Extension):
            def __init__(self):
                super().__init__()

            @GoldyBot.command()
            async def hello(self, platter: GoldyBot.GoldPlatter):
                await platter.send_message("👋hello", reply=True)

        def load():
            YourExtension()

    More at our `docs`_.

    .. _docs: https://goldybot.devgoldy.xyz/goldy.extensions.html#how-to-create-an-extension
    """

    def __init__(self):
        """Tells Goldy Bot to Load this class as an extension."""
        self.goldy: Goldy = get_goldy_instance()

        self.logger = LoggerAdapter(
            LoggerAdapter(goldy_bot_logger, prefix = "Extensions"), 
            prefix = Colours.GREY.apply(self.name)
        )

        # Cached commands list.
        self.commands: List[Command] = [

        ]

        self.__loaded_path = os.path.realpath(self.__class__.__module__) + ".py"
        self.__metadata = self.goldy.extension_loader.phrase_pyproject(self.__loaded_path)

        if self.name.lower() in [extension.lower() for extension in self.goldy.config.ignored_extensions]:
            self.logger.info(f"Not loading the extension '{self.name}' as it's ignored.")
            return False

        # Adding to cache and loading commands.
        # ---------------------------------------        
        extensions_cache.append(
            (self.name, self)
        )

        self.logger.info("Extension initialized!")

    @property
    def name(self) -> str:
        """Name of extension."""
        return self.__class__.__name__

    @property
    def loaded_path(self) -> str:
        """The path where this extension was loaded."""
        return self.__loaded_path
    
    @property
    def metadata(self) -> ExtensionMetadata | None:
        """Returns some metadata if available about this extension. Returns None if not available."""
        return self.__metadata

    @property
    def is_disabled(self) -> bool:
        """Returns true/false whether the extension is disabled. An extension is considered disabled when all of it's commands are also disabled."""
        if all([command.is_disabled for command in self.commands]):
            return True

        # I hope this doesn't fuck with us in the future. :)

        return False
    
    def disable(self) -> None:
        """A method to disable this extension."""
        self.logger.info("Disabling all commands in extension...")
        for command in self.commands:
            command.disable()
            self.logger.debug(f"Disabled '{command.name}'.")

        return None
    
    def enable(self) -> None:
        """A method to enable this extension."""
        self.logger.info("Enabling all commands in extension...")
        for command in self.commands:
            self.logger.debug(f"Enabled '{command.name}'.")
            command.enable()

        return None

    def unload(self) -> None:
        """
        Unloads and deletes itself from cache and all the commands with it. 
        You won't be able to load the extension again without the load path.
        """
        for command in self.commands:
            command.delete()

        extensions_cache.remove(
            (self.name, self)
        )

        self.logger.debug(f"Extension '{self.name}' unloaded!")

        return None