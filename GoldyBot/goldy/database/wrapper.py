from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from devgoldyutils import DictClass
from . import DatabaseEnums

if TYPE_CHECKING:
    from .. import objects
    from ..guilds import Guild


class DatabaseWrapper(DictClass):
    """✨ A useful class for interfacing with member data, guild data and more from the database."""
    def __init__(self, object: objects.Member | Guild, logger: logging.Logger = None) -> None:
        self.object = object
        self.goldy = object.goldy
        self.data = object.db_data

        super().__init__(logger)

    # TODO: Generate member data collections if they don't exist for the member.

    async def update(self) -> None:
        if isinstance(self.object, objects.Member):
            database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MEMBER_DATA)

            # Let's hope you are not in more than 200 guilds or else this will break! 😫
            member_data = await database.find(self.object.id, 
                query = {
                    "_id" : {"$in" : ["1", self.object.guild.id]}
                }, 
                key = "_id",
                max_to_find = 2
            )

            self.data = {**member_data[0], **member_data[1]}

        elif isinstance(self.goldy, Guild):
            database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MAIN)

            self.data = await database.find_one("guild_configs", query = {"_id": self.id})

        # More soon:tm:

        return None