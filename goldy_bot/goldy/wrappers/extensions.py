from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple

    from ..goldy import Goldy
    from ...extensions import Extension
    from ...typings import ExtensionLoadFuncT, ExtensionMetadataData

import sys
import toml
import importlib.util
from pathlib import Path
from devgoldyutils import shorter_path

from ...errors import GoldyBotError

__all__ = (
    "ExtensionsWrapper",
)

class ExtensionsWrapper():
    """Brings valuable methods to the goldy class for managing extensions."""
    def __init__(self) -> None:
        self.extensions: List[Extension] = []

        super().__init__()

    def add_extension(self: Goldy, extension: Extension) -> None:
        """Method to add an extension to the framework."""
        self.extensions.append(extension)

        self.logger.info(
            f"The extension '{extension.name}' has been added!"
        )

    def load_extension(self: Goldy, extension_path: Path, legacy: bool = False) -> Optional[Extension]:
        """Loads an extension from that path and returns it."""
        extension: Extension = None

        path = self.__get_extension_module(extension_path)
        shortened_path = shorter_path(path)

        self.logger.debug(f"Loading the extension at '{path}'...")

        spec_module = importlib.util.spec_from_file_location(str(path)[:-3], path)
        module_py = importlib.util.module_from_spec(spec_module)

        sys.modules[module_py.__name__] = module_py

        self.logger.debug(f"Executing extension at '{shortened_path}'...")

        try:
            spec_module.loader.exec_module(module_py)

        except Exception as e:
            msg = f"Error occurred while executing the extension at '{shortened_path}'. Error -> {e}"

            if self.config.extensions_raise_on_load_error:
                raise GoldyBotError(msg)

            self.logger.error(msg + " This extension will not be loaded!")
            return None

        self.logger.debug("Calling it's 'load' function...")
        load_function: ExtensionLoadFuncT = getattr(module_py, "load", None)

        if load_function is None:
            msg = f"The load function for the extension at '{shortened_path}' couldn't be found! " \
                "Make sure there is a load function in __init__.py"
            
            if self.config.extensions_raise_on_load_error:
                raise GoldyBotError(msg)

            self.logger.error(msg + " This extension will not be added!")
            return None

        extension = load_function(self) if load_function.__code__.co_argcount > 0 else load_function()

        if legacy is True:
            self.logger.debug("Called the extension load function successfully!")
        else:
            self.logger.debug(f"Called the '{extension.name}' extension load function successfully!")

        return extension

    def _get_extension_metadata(self: Goldy, extension_path: Path) -> Optional[ExtensionMetadataData]:
        root_path = extension_path.parent

        if "pyproject.toml" not in root_path.iterdir():
            self.logger.info(
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

    def __check_extension_legibility(self: Goldy, path: Path, metadata: ExtensionMetadataData) -> Tuple[bool, str]:
        # TODO: Make sure all pancake extensions that aren't just a file have a pyproject.toml file with the goldy bot version set.
        # TODO: If extension is depending a newer framework version raise exception, if it's pre-pancake give the user a warning that pre-pancake is deprecated.
        self.logger.debug("Checking if extension is legible...")
        ...