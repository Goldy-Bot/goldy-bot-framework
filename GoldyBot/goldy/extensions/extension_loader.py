from __future__ import annotations

import os
import sys
import toml
import pathlib
import pkg_resources
from typing import List, overload, TYPE_CHECKING, Dict, Tuple
import importlib.util

from .. import Goldy, GoldyBotError
from ... import goldy_bot_logger, LoggerAdapter
from ...paths import Paths
from . import extensions_cache
from .extension_metadata import ExtensionMetadata

if TYPE_CHECKING:
    from . import Extension

class ExtensionLoader():
    """Class that handles extension loading and reloading."""
    def __init__(self, goldy: Goldy, raise_on_load_error: bool | None = True) -> None:
        self.goldy = goldy
        self.raise_on_load_error = raise_on_load_error

        if self.raise_on_load_error is None:
            self.raise_on_load_error = self.goldy.config.raise_on_extension_loader_error

        self.path_to_extensions_folder:str|None = (lambda x: os.path.abspath(x) if isinstance(x, str) else x)(goldy.config.extension_folder_location)

        self.ignored_extensions = goldy.config.ignored_extensions
        self.late_load_extensions = goldy.config.late_load_extensions + ["guild_admin.py"]

        self.logger = LoggerAdapter(goldy_bot_logger, prefix="ExtensionLoader")

        self.__installed_dependencies = {pkg.key for pkg in pkg_resources.working_set}

    @overload
    def load(self) -> None:
        """Loads all extensions goldy bot can find. Basically lets goldy bot search for extensions herself because your a lazy brat."""
        ...
    
    @overload
    def load(self, extension_paths: List[str]) -> None:
        """Loads each extension in this list of paths."""
        ...

    def load(self, extension_paths: List[str] = None) -> None:
        """Loads each extension in this list of paths. If extension_paths is kept none, goldy bot will search for extensions to load itself."""
        if extension_paths is None:
            extension_paths = self.__find_all_paths()

        # self.check_dependencies() # TODO: Add method that checks dependencies from pyproject.toml and installs them if they are missing.

        for path in extension_paths:
            # Specify and get the module.
            self.logger.debug(f"Loading the extension at '{path}'...")
            spec_module = importlib.util.spec_from_file_location(path[:-3], path)
            module_py = importlib.util.module_from_spec(spec_module)

            # Pip install extension missing dependencies.
            for dependency in self.__check_dependencies(path):
                self.logger.info(f"Installing '{dependency[0]}'...")
                os.system(f'pip install "{dependency[1]}"')

            # Run module and load function.
            try:
                # For some reason if I don't do this shit blows up. (extensions won't be able to import modules in it's own directories)
                sys.modules[module_py.__name__] = module_py

                # Run module.
                self.logger.debug(f"Running extension at '{path}'...") # TODO: Change path to extension name for better logging maybe.
                spec_module.loader.exec_module(module_py)

                # Run load function.
                self.logger.debug(f"Calling the 'load()' function in the extension at {path}...")
                load_function = getattr(module_py, "load")
                load_function()

                self.logger.debug("Successfully ran the load function!")
            except Exception as e:
                if isinstance(e, AttributeError):
                    error_str = \
                        f"We encountered an error while trying to load the extension at '{'/'.join(path.split(os.path.sep)[-2:])}'! " \
                        f"\nYou likely forgot the 'load()' function. " \
                        "Check out https://goldybot.devgoldy.xyz/goldy.extensions.html#how-to-create-an-extension" \
                        f"\nERROR --> {e}"
                else:
                    error_str = \
                        f"We encountered an error while trying to load the extension at '{'/'.join(path.split(os.path.sep)[-2:])}'! " \
                        f"\nERROR --> {e}"
                
                if self.raise_on_load_error:
                    raise GoldyBotError(error_str)
                else:
                    self.logger.error(error_str)

        # TODO: Find a very lite way to return a list of extensions that were loaded somehow.
        # I could do this by returning a list of tuples from self.__find_all_paths() that contain the extension's name and path instead of just path.
        return None


    @overload
    async def reload(self) -> None:
        """Reloads all extensions loaded in goldy bot."""
        ...

    @overload
    async def reload(self, extensions: List[Extension]) -> None:
        """Reloads each extension in the list."""
        ...

    async def reload(self, extensions: List[Extension] = None) -> None:
        """Reloads each extension in this list. If extensions is kept none, goldy bot will reload all the extensions loaded itself."""
        if extensions is None:
            extensions = [x[1] for x in extensions_cache]

        loaded_paths = []

        self.logger.info(f"Reloading these extensions --> {[x.name for x in extensions]}")

        for extension in extensions:
            # Unload all commands in extension.
            extension.unload()

            # Get the full path the extension was loaded from so we can load it again with ExtensionLoader().
            if extension.loaded_path not in loaded_paths:
                loaded_paths.append(extension.loaded_path)

        self.load(loaded_paths)

        # Load commands again.
        await self.goldy.command_loader.load()

        return None

    def phrase_pyproject(self, extension_path: str) -> ExtensionMetadata | None:
        """Phrases the pyproject.toml file in that extension path."""
        if not extension_path.endswith("__init__.py"): 
            return None

        try:
            pyproject_toml: Dict[str, str] = toml.load(
                open(os.path.split(extension_path)[0] + "/pyproject.toml")
            )

            return ExtensionMetadata(pyproject_toml)

        except FileNotFoundError:
            self.logger.info(
                f"Couldn't phrase pyproject.toml for the extension at '{extension_path}' as it's directory does not contain a pyproject.toml file."
            )

        return None

    def __check_dependencies(self, extension_path: str) -> List[Tuple[str, str]]:
        """Returns list of missing dependencies needed to execute the extension."""
        missing_dependencies = []

        # Dependency check only works with extensions that are packages and contain a pyproject.toml file in their directory.
        if extension_path.endswith("__init__.py"): 
            self.logger.debug(f"Checking missing dependencies for extension at '{extension_path}'...")

            extension_metadata = self.phrase_pyproject(extension_path)

            if extension_metadata is None:
                return []

            if extension_metadata.dependencies is None:
                raise GoldyBotError(
                    f"Umm, seems like we couldn't find 'dependencies' in the pyproject.toml file for the extension at '{extension_path}'.\n" \
                    "Make sure you are following PEP 621! (https://peps.python.org/pep-0621/)"
                )

            for dependency in extension_metadata.dependencies:
                dependency_with_install_operations = dependency

                for character in [">", "=", "^", "<"]:
                    dependency = dependency.split(character)[0]

                if dependency.lower() not in self.__installed_dependencies:
                    self.logger.warning(f"Missing dependency '{dependency}'.")
                    missing_dependencies.append(
                        (dependency, dependency_with_install_operations)
                    )
                else:
                    self.logger.debug(f"'{dependency}' dependency found.")

        return missing_dependencies

    def __find_all_paths(self) -> List[str]:
        """Searches for all extensions, internal and external then returns their paths."""
        external_path = None
        internal_path = Paths.INTERNAL_EXTENSIONS

        paths = []
        late_load_paths = []
        
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

            if path_object.exists() is False:
                self.logger.warn(f"Couldn't find extension folder path at '{path_object}'!")
                continue

            self.logger.info(f"Found extension folder at '{path}'.")

            for file in path_object.iterdir():
                if file.name == "__pycache__":
                    continue

                if file.is_file() or file.is_dir():

                    if file.is_dir():

                        if "__init__.py" not in [x.name for x in file.iterdir()]:
                            self.logger.warn(f"Extension module '{file.name}' has no __init__.py so I'm ignoring it...")
                            continue

                        load_path = os.path.join(str(file), "__init__.py")

                    else:
                        load_path = str(file)

                    if file.name in self.late_load_extensions:
                        self.logger.info(f"The extension '{file.name}' will load late (after all other extensions).")
                        late_load_paths.append(load_path)
                    else:
                        paths.append(load_path)
                    
                    self.logger.debug(f"Found the module '{file.name}' in extensions.")

        paths.extend(late_load_paths)
        return paths