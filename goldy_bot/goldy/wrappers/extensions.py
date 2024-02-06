from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from typing_extensions import Self

    from ...typings import ExtensionLoadFuncT, ExtensionMetadataData, GoldySelfT

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

NAUGHTY_CHARACTERS = [
    " ", "#", "%", "&", "{", "}", "<", ">", "*", "?", "/", "$", "!", "'", '"', ":", "@", "+", "`", "|", "="
]

logger = LoggerAdapter(
    goldy_bot_logger, prefix = "Extensions"
)

class Extensions():
    """Brings valuable methods to the goldy class for managing extensions."""
    def __init__(self) -> None:
        self.extensions: List[Extension] = []

        super().__init__()

    def add_extension(self: GoldySelfT[Self], extension: Extension) -> None:
        """Adds an extension to goldy bot's internal state."""
        self.extensions.append(extension)

        logger.info(
            f"The extension '{extension.name}' has been added!"
        )

    def is_extension_ignored(self: GoldySelfT[Self], extension: Extension) -> bool:

        for ignored_extension in self.config.ignored_extensions:

            if extension.name.lower() == ignored_extension.lower():
                return True

        return False


    def load_extension(self: GoldySelfT[Self], extension_path: Path, legacy: bool = False) -> Optional[Extension]:
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

            if isinstance(e, AttributeError): # Error hint for legacy extensions.
                msg += "\n HINT: We think this might be because you are attempting to run a legacy extension with legacy mode off. Try running with '--legacy'."

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

            passed, reason = self.__check_extension_legibility(extension, extension_path)

            if passed is False:
                raise_or_error(
                    f"The extension '{extension.name}' failed legibility check: {reason}",
                    condition = lambda: self.config.extensions_raise_on_load_error,
                    logger = logger
                )

            else:
                logger.debug(f"The extension '{extension.name}' passed the legibility check.")

        return extension

    def _get_extension_metadata(self: GoldySelfT[Self], extension_path: Path) -> Optional[ExtensionMetadataData]:
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

    def __check_extension_legibility(self: GoldySelfT[Self], extension: Extension, extension_path: Path) -> Tuple[bool, Optional[str]]:
        # TODO: Make sure all pancake extensions that aren't just a file have a pyproject.toml file with the goldy bot version set.
        # TODO: If extension is depending a newer framework version raise exception, if it's pre-pancake give the user a warning that pre-pancake is deprecated.
        logger.debug(f"Checking legibility of the extension at '{shorter_path(extension_path)}'...")

        # check if the name is halal...
        for char in extension.name:

            if char in NAUGHTY_CHARACTERS: # Doesn't cover every character because goldy bot isn't for DUMB USERS IT'S FOR DEVELOPERS!
                return False, f"'{char}' is not allowed in extension name as it's a forbidden file character!"

        # shout at the user if the extension directory/module name is not the same as the actual extension name.
        if not extension_path.name == extension.name:
            return False, "extension name has to be the same as the extension's module!"

        # is there a fucking pyproject.toml file.
        files_in_dir = [path.name for path in extension_path.iterdir()]

        if "pyproject.toml" not in files_in_dir:
            return False, "pyproject.toml file is missing!"

        return True, None