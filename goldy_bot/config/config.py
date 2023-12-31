from __future__ import annotations
from typing import TYPE_CHECKING, cast
from .typing import ConfigData

if TYPE_CHECKING:
    from typing import List, Optional
    from .typing import VersionT

import toml
from dataclasses import dataclass, field

__all__ = (
    "Config",
)

@dataclass
class Config():
    """Class that provides interface for the goldy.toml file."""
    path: str
    data: ConfigData = field(repr = False, default = None)

    branding_name: str = field(init = False)
    included_extensions: List[str] = field(init = False)
    """Returns the extensions that were set to be included by the goldy.toml configuration."""
    repos: List[str] = field(init = False)
    """Returns the repositories goldy bot should pull from."""
    ignored_extensions: List[str] = field(init = False)
    """Returns ignored extensions specified in goldy.toml configuration."""
    extensions_directory: str = field(init = False)
    """Returns location set for the extension folder in the goldy.toml configuration."""
    extensions_raise_on_load_error: bool = field(init = False)
    """Returns whether the extension loader should raise on load errors stopping the entire framework or not."""
    test_guild_id: Optional[str] = field(init = False)
    developer_id: Optional[str] = field(init = False)
    """The discord id of the bot developer."""
    version: VersionT = field(init = False)

    def __post_init__(self):

        if self.data is None:

            with open(self.path, "r") as file:
                self.data = toml.load(file)

        self.data = cast(ConfigData, self.data)
        self.version = self.data.get("version")

        branding_data = self.data.get("branding", {})
        extensions_data = self.data.get("extensions", {})
        extensions_load_data = extensions_data.get("load", {})
        development_data = self.data.get("development", {})

        self.branding_name = branding_data.get("name", "GoldyBot")
        self.included_extensions = extensions_data.get("include", [])
        self.repos = extensions_data.get("repos", [])
        self.ignored_extensions = extensions_data.get("ignore", [])
        self.extensions_directory = extensions_load_data.get("directory", "./extensions")
        self.extensions_raise_on_load_error = extensions_load_data.get("raise_on_error", True)
        self.test_guild_id = development_data.get("test_guild_id")
        self.developer_id = development_data.get("developer_id")
        """The discord id of the bot developer."""