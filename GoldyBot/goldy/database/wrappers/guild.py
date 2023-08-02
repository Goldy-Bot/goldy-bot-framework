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

            "roles": {

            },

            "channels": {

            },

            "extensions": {
                "allowed": [],
                "disallowed": []
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
    def hidden_extensions(self) -> List[str]:
        """Returns the hidden extensions from this guild."""
        return self.get("extensions", "hidden")

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
        guild_config = await database.find_one("guild_configs", query = {"_id": self.guild.id})

        if guild_config is None:
            guild_config = guild_config_template
            await database.insert("guild_configs", data = guild_config)

        else:
            # Check if any keys are missing in the guild config, if any are update the config with the new item.
            # ---------------------------------------------------------------------------------------------------
            if not guild_config_template.keys() == guild_config.keys():
                
                # If there is an item in the template that isn't in the database add it.
                for item in guild_config_template:

                    if item not in guild_config:
                        guild_config[item] = guild_config_template[item]
                        self.logger.debug(
                            f"Added key '{item}' to {self.guild.code_name}'s database config because it was missing."
                        )

                await database.edit("guild_configs", query = {"_id": self.guild.id}, data = guild_config)


        self.data = guild_config