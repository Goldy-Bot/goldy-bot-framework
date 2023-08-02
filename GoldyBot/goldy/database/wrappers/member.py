from __future__ import annotations
from typing import Literal, TYPE_CHECKING

from . import DatabaseWrapper

from .. import DatabaseEnums

if TYPE_CHECKING:
    from ... import objects

class MemberDBWrapper(DatabaseWrapper):
    """A database wrapper for goldy bot members."""
    def __init__(self, member: objects.Member) -> None:
        self.member = member

        super().__init__(
            member.goldy, member.logger
        )

    async def push(self, type: Literal[DatabaseEnums.MEMBER_GUILD_DATA, DatabaseEnums.MEMBER_GLOBAL_DATA] | str, data: dict) -> None:
        self.logger.info("Pushing data to the database...")
        database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MEMBER_DATA)

        if isinstance(type, str):
            type = DatabaseEnums(type)

        doc_id = "1" # Global document.

        if type == DatabaseEnums.MEMBER_GUILD_DATA:
            doc_id = self.member.guild.id

        await database.edit(self.member.id, {"_id": doc_id}, data, overwrite = False)

    async def update(self) -> None:
        self.logger.info("Pulling updated member data from database...")

        database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MEMBER_DATA)

        # Let's hope you are not in more than 200 guilds or else this will break! 😫
        self.logger.debug("Finding member's data collections...")
        member_data = await database.find(self.member.id, 
            query = {
                "_id" : {"$in" : ["1", self.member.guild.id]}
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

            elif data["_id"] == self.member.guild.id:
                guild_data = data
                self.logger.debug(
                    f"Found member's guild data for '{self.member.guild.code_name}'."
                )

        # Generate template if member's data don't exist.
        # ------------------------------------------------
        if global_data is None:
            self.logger.info(
                f"'{self.member.username}'s global member data doesn't exist so we are generating one..."
            )

            await database.create_collection(
                self.member.id,
                data = {
                    "_id": "1",
                }
            )

            global_data = {"_id": "1"}

        if guild_data is None:
            self.logger.info(
                f"'{self.member.username}'s guild member data doesn't exist so we are generating one..."
            )

            await database.create_collection(
                self.member.id,
                data = {
                    "_id": self.member.guild.id,
                }
            )

            guild_data = {"_id": self.member.guild.id}


        self.data = {**global_data, **guild_data}