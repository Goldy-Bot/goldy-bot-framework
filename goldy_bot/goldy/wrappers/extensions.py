from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from typing_extensions import Self

    from ...typings import ExtensionLoadFuncT, ExtensionMetadataData, GoldySelfT

import sys
import toml
import subprocess
import importlib.util
from pathlib import Path
import importlib_metadata
from packaging import version
from devgoldyutils import shorter_path, LoggerAdapter

import goldy_bot
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

        self.__installed_dependencies: List[str] = [x.name for x in importlib_metadata.distributions()]

        super().__init__()

    def add_extension(self: GoldySelfT[Self], extension: Extension, internal: bool = False) -> None:
        """Adds an extension to goldy bot's internal state."""
        self.extensions.append(extension)

        extension.internal = internal

        logger.info(
            f"The extension '{extension.name}' has been added!"
        )

    def is_extension_ignored(self: GoldySelfT[Self], extension: Extension) -> bool:

        for ignored_extension in self.config.ignored_extensions:

            if extension.name.lower() == ignored_extension.lower():
                return True

        return False

    def _load_extension(self: GoldySelfT[Self], extension_path: Path, legacy: bool = False) -> Optional[Extension]:
        """Loads an extension from that path and returns it."""
        extension: Extension = None

        path = self.__get_extension_module_path(extension_path)
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
        pyproject_toml = None

        root_path = self.__get_extension_module_path(extension_path).parent

        for path in root_path.iterdir():

            if "pyproject.toml" == path.name:
                pyproject_toml = toml.load(path)["project"]

                if pyproject_toml.get("name") is None:
                    pyproject_toml["name"] = root_path.name

                break

        return pyproject_toml

    def _install_missing_extension_deps(
        self: GoldySelfT[Self], 
        extension_metadata: ExtensionMetadataData, 
        raise_on_framework_mismatch: bool
    ) -> None:
        dependencies_to_install = self.__get_missing_dependencies(
            extension_metadata, raise_on_framework_mismatch
        )

        if not dependencies_to_install == []:
            logger.info(f"Installing missing dependencies for extension '{extension_metadata['name']}'...")

            popen = subprocess.Popen( # TODO: We'll probably need to make the "pip" binary call configurable here.
                [sys.executable, "-m", "pip", "install"] + [dependency_version_tag for _, dependency_version_tag in dependencies_to_install] + ["-U"]
            )

            popen.wait()

    def __get_missing_dependencies(self, extension_metadata: ExtensionMetadataData, raise_on_framework_mismatch: bool) -> List[Tuple[str, str]]:
        """Returns list of missing dependencies needed to execute the extension."""
        missing_dependencies = []

        extension_dependencies: List[str] = extension_metadata.get("dependencies", [])

        for dependency in extension_dependencies:
            dependency_name = dependency
            dependency_version = dependency

            for character in [">", "=", "^", "<", "@git+"]:
                dependency_name = dependency_name.split(character)[0]
                dependency_version = dependency_version.split(character)[-1]

            if dependency_name == "GoldyBot":
                dependency_version = None if dependency_version == dependency_name or "http" in dependency_version else dependency_version

                if dependency_version is not None and version.parse(dependency_version) > version.parse(goldy_bot.__version__):
                    msg = f"Extension is expecting a newer version ({dependency_version}) of the Goldy Bot Framework. " \
                            f"We are currently running '{goldy_bot.__version__}'."

                    raise_or_error(
                        msg, 
                        condition = lambda: raise_on_framework_mismatch, 
                        logger = logger
                    )

                continue

            if dependency_name not in self.__installed_dependencies:
                logger.debug(f"Missing the dependency '{dependency_name}'.")
                missing_dependencies.append(
                    (dependency_name, dependency)
                )

            else:
                logger.debug(f"'{dependency_name}' dependency found.")

        return missing_dependencies

    def __get_extension_module_path(self, extension_path: Path):
        if not extension_path.is_file():
            extension_path = extension_path.joinpath("__init__.py")

        return extension_path

    def __check_extension_legibility(self: GoldySelfT[Self], extension: Extension, extension_path: Path) -> Tuple[bool, Optional[str]]:
        # TODO: If extension is depending on a newer framework version raise exception, if it's pre-pancake give 
        # the developer a warning that pre-pancake is deprecated.

        logger.debug(f"Checking legibility of the extension at '{shorter_path(extension_path)}'...")

        # shout at the developer if the extension directory/module name is not the same as the actual extension name.
        # -------------------------------------------------------------------------------------------------------------
        if not extension_path.name == extension.name:
            return False, "extension name has to be the same as the extension's module! " \
                "E.g. 'extensions/owo_extension/__init__.py' -> 'owo_extension'."

        # is there a fucking pyproject.toml file.
        # ----------------------------------------
        files_in_dir = [path.name for path in extension_path.iterdir()]

        if "pyproject.toml" not in files_in_dir:
            return False, "pyproject.toml file is missing! In pancake extensions must contain at least a minimal pyproject.toml."

        # warn the developer if they forget to mount a class housing commands.
        # ----------------------------------------------------------------------
        classes_mounted: List[str] = [x.__class__.__name__ for x in extension._classes]

        for class_name in extension._commands:

            if class_name not in classes_mounted:
                return False, f"The class '{class_name}' in '{extension.name}' needs to be mounted as it houses goldy bot commands!"

        return True, None