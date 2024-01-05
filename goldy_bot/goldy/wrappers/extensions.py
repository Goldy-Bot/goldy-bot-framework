from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple

    from ..goldy import Goldy
    from ...typings import ExtensionLoadFuncT, ExtensionMetadataData
    from ...commands import Command

import sys
import toml
import importlib.util
from pathlib import Path
from devgoldyutils import shorter_path, LoggerAdapter

from ...errors import raise_or_error
from ...extensions import Extension
from ...logger import goldy_bot_logger

__all__ = (
    "Extensions",
)

logger = LoggerAdapter(
    goldy_bot_logger, prefix = "Extensions"
)

class Extensions():
    """Brings valuable methods to the goldy class for managing extensions."""
    def __init__(self) -> None:
        self.extensions: List[Extension] = []

        super().__init__()

    def add_extension(self: Goldy, extension: Extension) -> None:
        """Adds an extension to goldy bot's internal state."""
        self.extensions.append(extension)

        logger.info(
            f"The extension '{extension.name}' has been added!"
        )

    def load_extension(self: Goldy, extension_path: Path, legacy: bool = False) -> Optional[Extension]:
        """Loads an extension from that path and returns it."""
        extension: Extension = None

        path = self.__get_extension_module(extension_path)
        shortened_path = shorter_path(path)

        logger.debug(f"Loading the extension at '{path}'...")

        spec_module = importlib.util.spec_from_file_location(str(path)[:-3], path)
        module_py = importlib.util.module_from_spec(spec_module)

        sys.modules[module_py.__name__] = module_py

        logger.debug(f"Executing extension at '{shortened_path}'...")

        try:
            spec_module.loader.exec_module(module_py)

        except Exception as e:
            msg = f"Error occurred while executing the extension at '{shortened_path}'. Error -> {e}"

            raise_or_error(
                msg, 
                condition = lambda: self.config.extensions_raise_on_load_error, 
                logger = logger
            )

            return None

        logger.debug("Calling it's 'load' function...")
        load_function: ExtensionLoadFuncT = getattr(module_py, "load", None)

        if load_function is None:
            msg = f"The load function for the extension at '{shortened_path}' couldn't be found! " \
                "Make sure there is a load function in __init__.py"

            raise_or_error(
                msg, 
                condition = lambda: self.config.extensions_raise_on_load_error, 
                logger = logger
            )

            return None

        extension = load_function(self) if load_function.__code__.co_argcount > 0 else load_function()

        if legacy is True: # when running in legacy mode extension can be none.

            if not isinstance(extension, Extension):
                extension = None # some legacy extensions are using lambda expressions so they tend to return a class instead of None.

            logger.debug("Called the extension load function successfully!")

        else:

            logger.debug(f"Called the '{extension.name}' extension load function successfully!")

            passed, reason = self.__check_extension_legibility(extension_path)

            if passed is False:
                raise_or_error(
                    f"The extension '{extension.name}' failed legibility check: {reason}",
                    condition = lambda: self.config.extensions_raise_on_load_error,
                    logger = logger
                )

            else:
                logger.debug(f"The extension '{extension.name}' passed the legibility check.")

        return extension

    async def _sync_commands(self: Goldy) -> None:
        """
        Registers all the commands from each extension in goldy bot's internal state with discord if not registered already.
        Also removes commands from discord that are no longer registered within the framework.
        """
        commands_to_register: List[Command] = []

        for extension in self.extensions:

            for commands in extension._commands.values():
                commands_to_register.extend(commands)

        test_guild_id = self.config.test_guild_id

        await self.create_application_commands(
            payload = [command.payload for command in commands_to_register], 
            guild_id = test_guild_id
        )

        logger.info("Commands have been registered with discord!")

    def _get_extension_metadata(self: Goldy, extension_path: Path) -> Optional[ExtensionMetadataData]:
        root_path = extension_path.parent

        if "pyproject.toml" not in root_path.iterdir():
            logger.info(
                f"Couldn't grab metadata from pyproject.toml for the extension at '{extension_path}' " \
                    "as it does not have a pyproject.toml file."
            )
            return None

        pyproject_toml = toml.load(
            root_path.joinpath("pyproject.toml"), encoding="UTF-8"
        )

        return pyproject_toml

    def __get_extension_module(self, extension_path: Path):
        if not extension_path.is_file():
            extension_path = extension_path.joinpath("__init__.py")

        return extension_path

    def __check_extension_legibility(self: Goldy, extension_path: Path) -> Tuple[bool, Optional[str]]:
        # TODO: Make sure all pancake extensions that aren't just a file have a pyproject.toml file with the goldy bot version set.
        # TODO: If extension is depending a newer framework version raise exception, if it's pre-pancake give the user a warning that pre-pancake is deprecated.
        logger.debug(f"Checking legibility of the extension at '{shorter_path(extension_path)}'...")

        files_in_dir = [path.name for path in extension_path.iterdir()]

        if "pyproject.toml" not in files_in_dir:
            return False, "pyproject.toml file is missing!"

        return True, None