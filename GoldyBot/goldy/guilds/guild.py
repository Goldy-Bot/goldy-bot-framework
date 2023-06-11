from __future__ import annotations

from typing import List, TYPE_CHECKING
from discord_typings import GuildData
from ..database import DatabaseEnums
from .. import nextcore_utils

if TYPE_CHECKING:
    from .. import Goldy
    from ... import Extension

class Guild():
    """A goldy bot guild."""
    def __init__(self, db_data: dict, goldy: Goldy) -> None:
        self.goldy = goldy
        self.db_data = db_data

    @property
    def id(self) -> str:
        """The guild's discord id"""
        return self.db_data["_id"]

    @property
    def code_name(self) -> str:
        """The goldy bot code name of the guild."""
        return self.db_data["code_name"]

    @property
    def prefix(self) -> str:
        """The prefix the guild uses."""
        return self.db_data["prefix"]
    
    @property
    def roles(self):
        return self.db_data["roles"]
    
    @property
    def channels(self):
        return self.db_data["channels"]
    
    @property
    def allowed_extensions(self) -> List[str]:
        """Returns the allowed extensions from this guild."""
        return self.db_data["extensions"]["allowed"]
    
    @property
    def disallowed_extensions(self) -> List[str]:
        """Returns the disallowed extensions from this guild."""
        return self.db_data["extensions"]["disallowed"]
    
    @property
    def hidden_extensions(self) -> List[str]:
        """Returns the hidden extensions from this guild."""
        return self.db_data["extensions"]["hidden"]
    
    def is_extension_allowed(self, extension: Extension) -> bool:
        """Returns True/False if this extension is allowed to function in this guild."""
        disallowed_extensions = [ext.lower() for ext in self.disallowed_extensions]

        if extension.name.lower() in disallowed_extensions:
            return False
        
        if len(disallowed_extensions) >= 1:

            if disallowed_extensions[0] == "." and extension.name.lower() not in [ext.lower() for ext in self.allowed_extensions]:
                return False
        
        return True
    
    async def get_guild_data(self) -> GuildData:
        """Returns discord's guild data; the same as :py:meth:`~GoldyBot.goldy.nextcord_utils.get_guild()`."""
        return await nextcore_utils.get_guild_data(self)

    async def update(self) -> None:
        """Updates guild's data by fetching from database."""
        database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MAIN)

        self.db_data = await database.find_one("guild_configs", query = {"_id": self.id})

        return None