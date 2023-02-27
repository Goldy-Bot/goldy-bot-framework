from __future__ import annotations

import os
import pathlib
from typing import List, overload
import importlib.util

from .. import Goldy, GoldyBotError
from ... import goldy_bot_logger, LoggerAdapter
from ...paths import Paths

class ExtensionLoader():
    """Class that handles extension loading."""
    def __init__(self, goldy:Goldy, raise_on_load_error:bool|None = True) -> None:
        self.goldy = goldy
        self.raise_on_load_error = raise_on_load_error

        if self.raise_on_load_error is None:
            self.raise_on_load_error = self.goldy.config.raise_on_extension_loader_error

        self.path_to_extensions_folder:str|None = (lambda x: os.path.abspath(x) if isinstance(x, str) else x)(goldy.config.extension_folder_location)
        self.ignored_extensions = goldy.config.ignored_extensions

        self.logger = LoggerAdapter(goldy_bot_logger, prefix="ExtensionLoader")

    def __find_all_paths(self) -> List[str]:
        """Searches for all extensions, internal and external then returns their paths."""
        external_path = None
        internal_path = Paths.INTERNAL_EXTENSIONS

        paths = []
        
        # Finding external extensions folder path if none.
        # -------------------------------------------------
        if self.path_to_extensions_folder is None:
            # Go look in the root dir.
            for file in os.listdir("."):
                if file == "extensions":
                    external_path = os.path.abspath(f"./{file}")
                    break
        else:
            external_path = self.path_to_extensions_folder

        # Getting all paths of each individual extension.
        # -------------------------------------------------
        for path in [external_path, internal_path]:
            path_object = pathlib.Path(path)

            if path_object.exists() == False:
                self.logger.warn(f"Couldn't find extension path at '{path_object}'!")
                continue

            self.logger.info(f"Found extension folder at '{path}'.")

            for file in path_object.iterdir():
                if file.name == "__pycache__":
                    continue

                if file.is_file() or file.is_dir():

                    if file.is_dir():
                        
                        if not "__init__.py" in [x.name for x in file.iterdir()]:
                            self.logger.debug(f"Module '{file.name}' has no __init__.py so I'm ignoring it...")
                            continue

                        paths.append(
                            os.path.join(file.__str__(), "__init__.py")
                        )

                    if file.is_file():
                        paths.append(file.__str__())
                    
                    self.logger.debug(f"Found the module '{file.name}' in extensions.")

        return paths

    @overload
    def load(self) -> None:
        """Loads all extensions goldy bot can find. Basically lets goldy bot search for extensions herself because your a lazy brat."""
        ...
    
    @overload
    def load(self, extension_paths:List[str]) -> None:
        """Loads each extension in this list of paths."""
        ...

    def load(self, extension_paths:List[str] = None) -> None:
        """Loads each extension in this list of paths. If extension_paths is kept none, goldy bot will search for extensions to load itself."""
        if extension_paths is None:
            extension_paths = self.__find_all_paths()

        for path in extension_paths:
            # Specify and get the module.
            spec_module = importlib.util.spec_from_file_location(path[:-3], path)
            module_py = importlib.util.module_from_spec(spec_module)
            
            # Run module.
            spec_module.loader.exec_module(module_py)

            # Get load function from module.
            try:
                self.logger.debug(f"Calling the 'load()' function in the extension at {path}...")
                load_function = getattr(module_py, "load")
                load_function()

                self.logger.debug("Successfully ran the load function!")
            except AttributeError as e:
                error_str = f"We encountered an error while trying to load extension at '{path}'! You most likely forgot the 'load()' function. \nERROR --> {e}"

                if self.raise_on_load_error:
                    raise GoldyBotError(error_str)

                else:
                    self.logger.error(error_str)
        
        # TODO: Find a very lite way to return a list of extensions that were loaded somehow.
        return None