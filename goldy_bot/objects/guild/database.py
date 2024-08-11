from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .guild import Guild

    SupportedValuesT = str | bool

from devgoldyutils import LoggerAdapter

from ...logger import goldy_bot_logger
from ...database import Database, DatabaseEnums
from ...database.database_wrapper import DatabaseWrapper, DatabaseWrapperDataT

__all__ = (
    "GuildDBWrapper",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "GuildDBWrapper")

class GuildDBWrapper(DatabaseWrapper[DatabaseWrapperDataT]):
    """A database wrapper for goldy bot guilds."""
    def __init__(self, database: Database, guild: Guild) -> None:
        self.__guild = guild

        super().__init__(database)

    async def push(self, data: dict) -> None:
        logger.info("Pushing guild data to the database...")

        database = self.database.get_database(DatabaseEnums.GOLDY_MAIN)
        guild_configs_collection = database.get_collection("guild_configs")

        await Database.edit(guild_configs_collection, {"_id": self.__guild.data["id"]}, data)

    async def update(self) -> None:
        logger.info(f"Pulling updated guild data for '{self.__guild.data['id']}'...")

        database = self.database.get_database(DatabaseEnums.GOLDY_MAIN)
        guild_configs_collection = database.get_collection("guild_configs")

        self.data = await guild_configs_collection.find_one({"_id": self.__guild.data["id"]})

    def get_extension_allowed(self, extension_name: str) -> bool:
        guild_configs: dict = self.get("configs", default = {})

        return guild_configs.get(f"extensions.{extension_name}.allow", False) 

    async def set_config(self, config_key: str, value: SupportedValuesT) -> None:
        if not isinstance(value, (bool, str)):
            raise TypeError(
                f"The value '{value}' ({type(value)}) is not supported on guild configs!"
            )

        guild_configs: dict = self.get("configs", {})

        guild_configs[config_key] = value

        await self.push(
            data = {
                "configs": guild_configs
            }
        )