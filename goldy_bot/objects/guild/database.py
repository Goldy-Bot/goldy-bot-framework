from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .guild import Guild

from devgoldyutils import LoggerAdapter

from ...logger import goldy_bot_logger
from ...database import Database, DatabaseEnums
from ...database.database_wrapper import DatabaseWrapper

__all__ = (
    "GuildDBWrapper",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "GuildDBWrapper")

class GuildDBWrapper(DatabaseWrapper):
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