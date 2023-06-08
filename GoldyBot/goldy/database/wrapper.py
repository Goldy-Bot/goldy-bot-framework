from __future__ import annotations

from typing import TYPE_CHECKING
from devgoldyutils import DictClass, LoggerAdapter, Colours
from . import DatabaseEnums
from .. import objects

if TYPE_CHECKING:
    from ..guilds import Guild


class DatabaseWrapper(DictClass):
    """✨ A useful class for interfacing with member data, guild data and more from the database."""
    def __init__(self, object: objects.Member | Guild) -> None:
        self.object = object
        self.goldy = object.goldy

        self.data = {}

        super().__init__(
            LoggerAdapter(object.logger, prefix=Colours.PINK_GREY.apply("Database Wrapper"))
        )

    async def update(self) -> None:
        self.logger.info("Pulling updated data from database...")

        if isinstance(self.object, objects.Member):
            member = self.object
            database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MEMBER_DATA)

            # Let's hope you are not in more than 200 guilds or else this will break! 😫
            self.logger.debug("Finding member's data collections...")
            member_data = await database.find(member.id, 
                query = {
                    "_id" : {"$in" : ["1", member.guild.id]}
                }, 
                key = "_id",
                max_to_find = 2
            )

            global_data = None
            guild_data = None

            for data in member_data:

                if data["_id"] == "1":
                    global_data = data
                    self.logger.debug("Found member's global data.")

                elif data["_id"] == member.guild.id:
                    guild_data = data
                    self.logger.debug(
                        f"Found member's guild data for '{member.guild.code_name}'."
                    )

            # Generate template if member's data don't exist.
            # ------------------------------------------------
            if global_data is None:
                self.logger.info(
                    f"'{member.username}'s global member data doesn't exist so we are generating one..."
                )

                await database.create_collection(
                    member.id,
                    data = {
                        "_id": "1",
                    }
                )

                global_data = {"_id": "1"}

            if guild_data is None:
                self.logger.info(
                    f"'{member.username}'s guild member data doesn't exist so we are generating one..."
                )

                await database.create_collection(
                    member.id,
                    data = {
                        "_id": member.guild.id,
                    }
                )

                guild_data = {"_id": member.guild.id}

            self.data = {**global_data, **guild_data}

        elif isinstance(self.goldy, Guild):
            database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MAIN)

            #self.data = await database.find_one("guild_configs", query = {"_id": self.id})

            # TODO: Move guild database stuff to this wrapper.

        # More soon:tm:

        return None