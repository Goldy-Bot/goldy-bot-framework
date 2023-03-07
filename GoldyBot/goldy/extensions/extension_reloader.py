from __future__ import annotations

import os
import pathlib
from typing import List, overload, TYPE_CHECKING
import importlib.util

from .. import Goldy, GoldyBotError
from ... import goldy_bot_logger, LoggerAdapter
from . import extensions_cache

if TYPE_CHECKING:
    from . import Extension

class ExtensionReloader():
    """Class that handles extension reloading."""
    def __init__(self, goldy:Goldy) -> None:
        self.goldy = goldy

        self.logger = LoggerAdapter(goldy_bot_logger, prefix="ExtensionReloader")

    @overload
    async def reload(self) -> None:
        """Reloads all extensions loaded in goldy bot."""
        ...
    
    @overload
    async def reload(self, extensions:List[Extension]) -> None:
        """Reloads each extension in the list."""
        ...

    async def reload(self, extensions:List[Extension] = None) -> None:
        """Reloads each extension in this list. If extensions is kept none, goldy bot will reload all the extensions loaded itself."""
        if extensions is None:
            extensions = [x[1] for x in extensions_cache]

        loaded_paths = []

        self.logger.info(f"Reloading these extensions --> {[x.code_name for x in extensions]}")

        for extension in extensions:
            # Delete all commands in extension.
            await extension.delete()

            if not extension.loaded_path in loaded_paths:
                loaded_paths.append(extension.loaded_path)

        self.goldy.extension_loader.load(loaded_paths)

        # Load commands again.
        await self.goldy.command_loader.load()

        return None