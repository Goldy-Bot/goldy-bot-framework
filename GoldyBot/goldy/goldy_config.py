from typing import List

from ..config import Config
from ..paths import Paths

class GoldyConfig(Config):
    """
    Class that allows you to retrieve configuration data from the ``goldy.json`` config file.

    All properties raise KeyError when not found in the config.
    """
    def __init__(self):
        super().__init__(Paths.GOLDY_JSON)

    @property
    def ignored_extensions(self) -> List[str]:
        """Returns code name of all ignored extensions from ``goldy.json``."""
        return self.get("goldy", "extensions", "ignored_extensions")

    @property
    def extension_folder_location(self) -> str:
        """Returns location set for the extension folder in ``goldy.json``."""
        return self.get("goldy", "extensions", "folder_location")

    #TODO: Add more properties.