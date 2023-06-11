from __future__ import annotations
import asyncio
from typing import List

from enum import Enum

import pymongo
from pymongo.errors import ServerSelectionTimeoutError
from devgoldyutils import Colours
import motor.motor_asyncio
from .. import Goldy, LoggerAdapter, goldy_bot_logger, GoldyBotError

from .databases import GoldyDB

class DatabaseEnums(Enum):
    """Enum class that holds the code names for all goldy bot pymongo databases and collection types."""
    GOLDY_MAIN = "goldy_main"
    GOLDY_MEMBER_DATA = "goldy_member_data"

    MEMBER_GUILD_DATA = "member_guild_data"
    MEMBER_GLOBAL_DATA = "member_global_data"

    def __init__(self, database_name: str):
        ...

class Database():
    """Goldy Bot's class to interface with a Mongo Database asynchronously."""
    def __init__(self, goldy: Goldy):
        self.goldy = goldy
        self.database_url = self.goldy.token.database_url
        self.async_loop = asyncio.get_event_loop()
        self.logger = LoggerAdapter(goldy_bot_logger, prefix="Database")

        # Initializing MongoDB database.
        try:
            self.client: pymongo.MongoClient = motor.motor_asyncio.AsyncIOMotorClient(self.database_url, serverSelectionTimeoutMS=2000)
            self.async_loop.run_until_complete(self.client.server_info())
            self.logger.info("AsyncIOMotorClient " + Colours.GREEN.apply_to_string("Connected!"))
        except ServerSelectionTimeoutError as e:
            raise GoldyBotError(
                f"Couldn't connect to Database! Check if the database URL you entered is correct. Error received from motor >>> {e}"
            )

        except Exception as e:
            raise GoldyBotError(
                f"Couldn't connect to Database! Error received from motor >>> {e}"
            )

    async def insert(self, database: DatabaseEnums | str, collection: str, data) -> bool:
        """Inserts the data provided into a collection in this database."""
        return await self.get_goldy_database(database).insert(collection, data)

    async def edit(self, database: DatabaseEnums | str, collection: str, query, data: dict) -> bool:
        """Finds and edits a document in this database and collection with the data provided."""
        return await self.get_goldy_database(database).edit(collection, query, data)

    async def remove(self, database: DatabaseEnums | str, collection: str, data) -> bool:
        """Finds and deletes a copy of this data from a collection in this database."""
        return await self.get_goldy_database(database).remove(collection, data)

    async def find(self, database: DatabaseEnums | str, collection: str, query, key: str, max_to_find = 50) -> List[dict]:
        """Searches for and returns documents with that query in a collection in this database."""
        return await self.get_goldy_database(database).find(collection, query, key, max_to_find)

    async def find_all(self, database: DatabaseEnums | str, collection: str, max_to_find = 100) -> List[dict] | None:
        """Finds and returns all documents in a collection from this database. This took me a day to make! 😞"""
        return await self.get_goldy_database(database).find_all(collection, max_to_find)

    async def find_one(self, database: DatabaseEnums | str, collection: str, query: dict) -> dict | None:
        """Searches for and returns specific data from a collection in this database."""
        return await self.get_goldy_database(database).find_one(collection, query)

    async def create_collection(self, database: DatabaseEnums | str, collection_name: str, data) -> bool:
        return await self.get_goldy_database(database).create_collection(collection_name, data)

    async def get_collection(self, database: DatabaseEnums | str, collection: str):
        """Returns cursor of the following collection."""
        return await self.get_goldy_database(database).get_collection(collection)

    async def delete_collection(self, database: DatabaseEnums | str, collection_name: str) -> bool:
        return await self.get_goldy_database(database).delete_collection(collection_name)

    async def list_collection_names(self, database: DatabaseEnums | str) -> List[str]:
        """Returns list of all collection name in this database."""
        return await self.get_goldy_database(database).list_collection_names()

    
    def get_goldy_database(self, database_name: DatabaseEnums | str) -> GoldyDB:
        """Returns an instance of :py:meth:`~GoldyBot.goldy.database.databases.GoldyDB`."""
        if isinstance(database_name, DatabaseEnums):
            return GoldyDB(self, database_name.value)

        return GoldyDB(self, DatabaseEnums(database_name).value)