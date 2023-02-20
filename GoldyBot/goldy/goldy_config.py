from typing import List

from ..config import Config
from ..errors import GoldyBotError

class GoldyConfig(Config):
    """
    Class that allows you to retrieve configuration data from the ``goldy.json`` config file.

    All properties return None when not found in the config.
    """
    def __init__(self):
        try:
            super().__init__("./goldy.json")
        except FileNotFoundError as e:
            raise GoldyBotError(
                f"Goldy config not found in root! Please create an environment with the command 'goldybot setup' in terminal. \nERROR -> {e}"
            )

    @property
    def ignored_extensions(self) -> List[str]:
        """Returns code name of all ignored extensions from ``goldy.json``."""
        return self.get("goldy", "extensions", "ignored_extensions")

    @property
    def extension_folder_location(self) -> str:
        """Returns location set for the extension folder in ``goldy.json``."""
        return self.get("goldy", "extensions", "folder_location")

    @property
    def raise_on_extension_loader_error(self) -> bool:
        """Returns whether the extension loader should raise on load errors stopping the entire framework or not."""
        return self.get("goldy", "extensions", "raise_on_load_error", default_value=True)

    #TODO: Add more properties.