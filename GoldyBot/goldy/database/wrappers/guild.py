from __future__ import annotations
from typing import TYPE_CHECKING, List

from . import DatabaseWrapper

from .. import DatabaseEnums

if TYPE_CHECKING:
    from ... import guilds

class GuildDBWrapper(DatabaseWrapper):
    """A database wrapper for goldy bot members."""
    def __init__(self, guild: guilds.Guild) -> None:
        self.guild = guild

        self.guild_config_template = {
            "_id": "",
            "code_name": "",

            "prefix": "!",

            "roles": {},

            "channels": {},

            "extensions": {
                "allowed": [],
                "disallowed": [],
                "restrictions" : {}
            }
        }

        super().__init__(
            guild.goldy, guild.logger
        )

    @property
    def prefix(self) -> str:
        """The prefix the guild uses."""
        return self.get("prefix")
    
    @property
    def roles(self):
        return self.get("roles")
    
    @property
    def channels(self):
        return self.get("channels")
    
    @property
    def allowed_extensions(self) -> List[str]:
        """Returns the allowed extensions from this guild."""
        return self.get("extensions", "allowed")
    
    @property
    def disallowed_extensions(self) -> List[str]:
        """Returns the disallowed extensions from this guild."""
        return self.get("extensions", "disallowed")

    @property
    def extension_restrictions(self) -> List[str]:
        """Returns the extension restrictions from this guild."""
        return self.get("extensions", "restrictions")

    async def push(self, data: dict) -> None:
        self.logger.info("Pushing guild config to the database...")
        database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MAIN)

        doc_id = self.guild.id

        await database.edit("guild_configs", {"_id": doc_id}, data, overwrite = False)

    async def update(self) -> None:
        self.logger.info("Pulling updated guild configuration data from database...")

        database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MAIN)

        # Setting up guild config.
        # -------------------------
        guild_config_template = self.guild_config_template.copy()
        guild_config_template["_id"] = self.guild.id
        guild_config_template["code_name"] = self.guild.code_name

        # Add guild to database.
        # -----------------------
        #guild_config = await database.find_one("guild_configs", query = {"_id": self.guild.id})

        #if guild_config is None:
        #    guild_config = guild_config_template
        #    await database.insert("guild_configs", data = guild_config)

        #else:
        guild_config = await database.edit(
            "guild_configs", query = {"_id": self.guild.id}, data = guild_config_template
        )

        self.data = guild_config