from __future__ import annotations
import asyncio
from typing import Any, Dict, List
import pymongo
import motor.motor_asyncio
from .. import Goldy, LoggerAdapter, goldy_bot_logger, GoldyBotError

MODULE_NAME = "DATABASE"

class Database():
    """Goldy Bot's class to interface with a Mongo Database."""
    def __init__(self, goldy:Goldy):
        self.goldy = goldy
        self.database_token_url = self.goldy.token.database_token
        self.async_loop = asyncio.get_event_loop()
        self.logger = LoggerAdapter(goldy_bot_logger, prefix="Database")

        # Initializing MongoDB database
        try:
            self.client:pymongo.MongoClient = motor.motor_asyncio.AsyncIOMotorClient(self.database_token_url, serverSelectionTimeoutMS=2000)
            self.async_loop.run_until_complete(self.client.server_info())
            self.database = self.client[
                #TODO: Get database name and dump it here.
            ]

        except Exception:
            raise GoldyBotError(
                "Couldn't connect to Database! Check the database URL you entered."
            )

    async def insert(self, collection:str, data) -> bool:
        """Tells database to insert the data provided into a collection."""
        await self.database[collection].insert_one(data)
        self.logger.debug(f"Inserted '{data}' into '{collection}.'")
        return True

    async def edit(self, collection:str, query, data:dict) -> bool:
        """Tells database to find and edit a document with the data provided in a collection."""
        await self.database[collection].update_one(query, {"$set": data})
        self.logger.debug(f"Edited '{query}' into '{data}.'")
        return True

    async def remove(self, collection:str, data) -> bool:
        """Tells database to find and delete a copy of this data from the collection."""
        await self.database[collection].delete_one(data)
        self.logger.debug(f"Deleted '{data}' from '{collection}.'")
        return True

    async def find(self, collection:str, query, key:str, max_to_find=50) -> List[dict]:
        """Searches for documents with the query."""
        try:
            document_list = []
            cursor = self.database[collection].find(query).sort(key)

            for document in await cursor.to_list(max_to_find):
                document_list.append(document)

            return document_list
        except KeyError as e:
            self.logger.debug(f"Could not find the collection '{collection}'!")
            return None

    async def find_all(self, collection:str, max_to_find=100) -> List[dict] | None:
        """Finds and returns all documents in a collection. This took me a day to make! 😞"""
        try:
            document_list = []
            cursor = self.database[collection].find().sort('_id')

            for document in await cursor.to_list(max_to_find):
                document_list.append(document)

            return document_list
        except KeyError as e:
            self.logger.debug(f"Could not find the collection '{collection}'!")
            return None

    async def get_collection(self, collection):
        """Returns cursor of the following collection."""
        return self.database[collection]

    async def list_collection_names(self) -> List[str]:
        """Returns list of all collection names."""
        return await self.database.list_collection_names()

    async def find_one(self, collection:str, query:dict) -> (dict | None):
        """Tells database to search for and return specific data from a collection."""
        data = await self.database[collection].find_one(query)

        if not data == None:
            self.logger.debug(f"Found '{query}' in '{collection}.'")
            return data
        else:
            self.logger.debug(f"'{query}' was not found in '{collection}.'")
            return None
        
    async def create_collection(self, collection_name:str, data):
        await self.database[collection_name].insert_one(data)
        self.logger.debug(f"Database collection '{collection_name}' created.")

    async def delete_collection(self, collection_name:str):
        await self.database[collection_name].drop()
        self.logger.debug(f"Database collection '{collection_name}' dropped.")

    def new_instance(self, database_name:str):
        """Starts a new database instance the efficient way. 👍"""
        class NewDatabase(Database):
            def __init__(self, database_self:Database):
                self.database = database_self.client[database_name]

        return NewDatabase(self)

