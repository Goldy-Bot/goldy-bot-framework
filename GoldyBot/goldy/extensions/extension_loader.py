import os
from typing import List, overload

from . import Extension

from .. import Goldy

class ExtensionLoader():
    """Class that handles extension loading."""
    def __init__(self, goldy:Goldy) -> None:
        self.path_to_extensions_folder:str = os.path.abspath(
            (lambda x: "." if x in [None, ""] else x)(goldy.config.extension_folder_location)
        )

    def find_all_paths(self) -> List[str]:
        """Searches for all extensions, internal and external then returns their paths."""
        
        ...

    @overload
    def load(self, extension_paths:List[str]) -> List[Extension]:
        """Loads all extensions in this list of paths."""
        ...

    @overload
    def load(self) -> List[Extension]:
        """Loads all extensions goldy bot can find."""
        ...

ExtensionLoader().load()