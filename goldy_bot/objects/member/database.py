from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from .member import Member
    
from devgoldyutils import LoggerAdapter

from ...logger import goldy_bot_logger
from ...database import Database, DatabaseEnums
from ...database.database_wrapper import DatabaseWrapper

__all__ = (
    "MemberDBWrapper",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "MemberDBWrapper")

class MemberDBWrapper(DatabaseWrapper):
    """A database wrapper for goldy bot members."""
    def __init__(self, database: Database, member: Member) -> None:
        self.member = member

        super().__init__(database)

    async def push(self, data: dict, guild_id: Optional[str] = None) -> None:
        logger.info("Pushing data to the database...")
        database = self.database.get_database(DatabaseEnums.GOLDY_MEMBER_DATA)

        doc_id = "1" # Global document.

        if guild_id is not None:
            doc_id = guild_id

        member_collection = database.get_collection(self.member.data["id"])

        await Database.edit(member_collection, {"_id": doc_id}, data)

    async def update(self, guild_id: Optional[str] = None) -> None:
        logger.info(f"Pulling updated member data for '{self.member.data['username']}'...")

        database = self.database.get_database(DatabaseEnums.GOLDY_MEMBER_DATA)
        member_collection = database.get_collection(self.member.data["id"])

        query = {"_id": "1"}

        if guild_id is not None:
            query = {"_id" : {"$in" : ["1", guild_id]}}

        member_data = await Database.find(member_collection, 
            query = query, 
            key = "_id", 
            max_to_find = 2
        )

        guild_data = {}
        global_data = {}

        for data in member_data:

            if data["_id"] == "1":
                global_data = data

            elif data["_id"] == guild_id:
                guild_data = data

        self.data = {**global_data, **guild_data}