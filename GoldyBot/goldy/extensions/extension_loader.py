import os
import pathlib
from typing import List, overload

from . import Extension

from .. import Goldy, GoldyBotError
from ...paths import Paths

class ExtensionLoader():
    """Class that handles extension loading."""
    def __init__(self, goldy:Goldy) -> None:
        self.path_to_extensions_folder:str = (lambda x: os.path.abspath(x) if isinstance(x, str) else x)(goldy.config.extension_folder_location)

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
            for file in pathlib.Path(path).iterdir():
                if file.is_file():
                    paths.append(file.__str__()) 
                    continue
                
                elif file.is_dir():
                    if "__init__" in file.iterdir():
                        paths.append(file.__str__())
                        continue

        return paths

    @overload
    def load(self, extension_paths:List[str]) -> List[Extension]:
        """Loads all extensions in this list of paths."""
        ...

    @overload
    def load(self) -> List[Extension]:
        """Loads all extensions goldy bot can find."""
        ...

print(
    ExtensionLoader().__find_all_paths()
)

raise GoldyBotError("STOP")