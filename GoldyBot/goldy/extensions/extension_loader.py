from __future__ import annotations
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from . import Extension
    from typing import List, Dict, Tuple, TypedDict

    EXTENSION_REPO_DATA = TypedDict("EXTENSION_REPO_DATA", {"id": str, "git_url": str})
    V1_REPO_DATA = TypedDict("V1_REPO_DATA", {"version": int, "extensions": List[EXTENSION_REPO_DATA]})

import os
import sys
import toml
import pathlib
import requests
import subprocess
import pkg_resources
import importlib.util
from packaging import version
from urllib.parse import urlparse
from devgoldyutils import LoggerAdapter

from ... import utils
from ...paths import Paths
from . import extensions_cache
from .. import Goldy, GoldyBotError
from .extension_metadata import ExtensionMetadata
from ... import goldy_bot_logger, __version__ as framework_version

class ExtensionLoader():
    """Class that handles extension loading and reloading."""
    def __init__(self, goldy: Goldy, raise_on_load_error: bool | None = True) -> None:
        self.goldy = goldy
        self.raise_on_load_error = raise_on_load_error

        if self.raise_on_load_error is None:
            self.raise_on_load_error = self.goldy.config.raise_on_extension_loader_error

        self.extensions_to_include = goldy.config.included_extensions
        self.path_to_extensions_folder: str | None = (lambda x: os.path.abspath(x) if isinstance(x, str) else x)(goldy.config.extension_folder_location)

        self.ignored_extensions = goldy.config.ignored_extensions
        self.late_load_extensions = goldy.config.late_load_extensions + ["guild_admin.py"]

        self.logger = LoggerAdapter(goldy_bot_logger, prefix="ExtensionLoader")

        self.__installed_dependencies = {pkg.key for pkg in pkg_resources.working_set}

    def pull(self, repos: List[str] = None) -> None:
        """
        Pulls down the extensions that you specified from a repo into your extensions folder if they don't already exist.
        """
        extensions = self.extensions_to_include

        if repos is None:
            repos = ["https://github.com/Goldy-Bot/goldybot.repo"] + self.goldy.config.extension_repos

        extensions_folder_path = self.__find_external_extension_path()

        self.logger.info("Getting goldy bot extensions repo...")
        repo_extensions: List[EXTENSION_REPO_DATA] = []

        for repo_url in repos:
            phrased_url = urlparse(repo_url)

            if "github.com" in phrased_url.netloc:
                repo_url = utils.get_github_file(phrased_url, "main", "repo.json")

            self.logger.debug(f"Making request to repo at '{repo_url}'...")
            r = requests.get(repo_url)

            if r.ok:
                repo_json: V1_REPO_DATA = r.json()
                repo_extensions += repo_json["extensions"]
            else:
                self.logger.error(f"Failed to get repo! Extensions in that repo will not be pulled! \nResponse: {r}")

        extensions_to_pull: List[Tuple[str, str]] = []

        for extension in extensions:

            for repo_extension in repo_extensions:

                if extension.lower() == repo_extension["id"]:
                    self.logger.debug(f"Found {extension} in repo.")
                    extensions_to_pull.append((repo_extension["id"], repo_extension["git_url"]))
                    break

        if ".git" not in os.listdir("."):
            self.logger.debug("Root directory is not git repo so I'm making it one.")
            os.system("git init")

        if ".gitmodules" not in os.listdir("."):
            self.logger.debug("No '.gitmodules' file in root so I'm creating one.")
            open(".gitmodules", "w").close()

        if ".gitattributes" not in os.listdir("."):
            self.logger.debug("No '.gitattributes' file in root so I'm creating one.")
            with open(".gitattributes", "w") as file:
                file.write("# Auto detect text files and perform LF normalization\n* text=auto")

        # If there is an submodule extension that exists but hasn't been included delete it.
        # =====================================================================================
        if self.goldy.system.in_docker:
            subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", "/app/goldy"]
            )

            self.logger.debug("Set root path to git's safe directory as you are running under docker.")

        git_submodule_output = subprocess.check_output(["git", "submodule"], encoding = "utf+8")

        submodule_extension_paths = [x[1:].split(" ")[1] for x in git_submodule_output.splitlines()]

        if sys.platform == "win32": # IDK WHY THE FUCK THAT COMMAND ABOVE MAKES ME LOOSE COLOUR ON WINDOWS!!! AUGHHHHHHHHHHHH!
            os.system("color")

        for extension_path in submodule_extension_paths:
            found = False
            extension = extension_path.split("/")[-1]

            for code_name, _ in extensions_to_pull:

                if extension == code_name:
                    found = True

            if not found:
                self.logger.warning(
                    f"Removing the '{extension}' submodule extension as you've no longer included it..."
                )

                os.system(f"git rm {extensions_folder_path}{os.path.sep}{extension} -f")
                self.logger.debug(f"git submodule '{extension}' removed.")

        # actually pulling submodules
        # =============================
        for code_name, git_url in extensions_to_pull:

            if os.path.exists(f"{extensions_folder_path}{os.path.sep}{code_name}"):
                self.logger.debug(f"'{code_name}' already exists so we will not git clone it.")
                continue

            self.logger.info(f"Git cloning '{code_name}' extension...")
            # NOTE: Ummm, should we use psutil instead?
            os.system(
                f'cd "{extensions_folder_path}" && git submodule add -f {git_url} {code_name}'
            )

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

                # Fix for https://github.com/Goldy-Bot/Goldy-Bot-Framework/issues/92
                for module_name in sys.modules.copy():
                    if f"{os.sep}extensions" in module_name:

                        if module_py.__name__ in module_name.split(f"{os.sep}extensions")[1]:
                            del sys.modules[module_name]
                            self.logger.debug(f"Deleted previous import for this extension. >> ({module_name})")

                    elif f"{os.sep}internal_extensions" in module_name:
                        if module_py.__name__ in module_name.split(f"{os.sep}internal_extensions")[1]:
                            del sys.modules[module_name]
                            self.logger.debug(f"Deleted previous import for this extension. >> ({module_name})")

                    elif module_py.__name__ in module_name:
                        del sys.modules[module_name]
                        self.logger.debug(f"Deleted previous import for this extension. >> ({module_name})")

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
                open(os.path.split(extension_path)[0] + "/pyproject.toml", encoding="UTF-8")
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
                dependency_name = dependency
                dependency_version = dependency

                for character in [">", "=", "^", "<", "@git+"]:
                    dependency_name = dependency_name.split(character)[0]
                    dependency_version = dependency_version.split(character)[-1]

                dependency_version = None if dependency_version == dependency_name or "http" in dependency_version else dependency_version

                if dependency_name == "GoldyBot": # Skip checking the goldy bot dependency.

                    if dependency_version is not None and version.parse(dependency_version) > version.parse(framework_version):
                        raise GoldyBotError(
                            f"Extension is expecting a newer version ({dependency_version}) of the Goldy Bot Framework. " \
                                f"We are currently running '{framework_version}'."
                        )

                    continue

                if dependency_name.lower() not in self.__installed_dependencies:
                    self.logger.warning(f"Missing dependency '{dependency_name}'.")
                    missing_dependencies.append(
                        (dependency_name, dependency)
                    )
                else:
                    self.logger.debug(f"'{dependency_name}' dependency found.")

        return missing_dependencies
    
    def __find_external_extension_path(self) -> str:
        if self.path_to_extensions_folder is not None:
            return self.path_to_extensions_folder

        # Go look in the root dir.
        for file in os.listdir("."):
            if file == "extensions":
                return os.path.abspath(f"./{file}")

        # NOTE: Idk why the hell I did it like this in the past so instead of changing something that works
        # and bricking the framework in the process let's just keep it the same but 
        # raise an informative exception incase things go haywire.
        raise GoldyBotError("Wait what, where the hell is the extensions folder.")

    def __find_all_paths(self) -> List[str]:
        """Searches for all extensions, internal and external then returns their paths."""
        external_path = None
        internal_path = Paths.INTERNAL_EXTENSIONS

        paths = []
        late_load_paths = []
        
        # Finding external extensions folder path if none.
        # -------------------------------------------------
        external_path = self.__find_external_extension_path()

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