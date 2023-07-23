from __future__ import annotations

from ... import LoggerAdapter
from .... import utils

from typing import List
from devgoldyutils import Colours

class GoldyDB():
    """A class representing a singular goldy bot database in mongoDB."""
    def __init__(self, core_database, db_code_name: str) -> None:
        self.client = core_database.client
        self.database = self.client[db_code_name]
        
        self.logger = LoggerAdapter(core_database.logger, Colours.PINK_GREY.apply_to_string(db_code_name))

    async def insert(self, collection: str, data) -> None:
        """
        Inserts the data provided into a collection in this database. 
        Creates a whole new document. If you want to edit an existing document use .edit()
        """
        await self.database[collection].insert_one(data)
        self.logger.debug(f"Inserted '{data}' into '{collection}.'")

    async def edit(self, collection: str, query, data: dict, overwrite: bool = True) -> None:
        """Finds and edits a document in this database and collection with the data provided."""
        if overwrite:
            await self.database[collection].update_one(query, {"$set": data})
        else:
            document_data = await self.find_one("guild_configs", query)
            new_data = utils.update_dict(document_data, data) # Override the document's data with the new data.
            await self.database[collection].update_one(query, {"$set": new_data})
        self.logger.debug(f"Edited '{query}' with '{data}.'")

    async def remove(self, collection: str, data) -> None:
        """Finds and deletes a copy of this data from a collection in this database."""
        await self.database[collection].delete_one(data)
        self.logger.debug(f"Deleted '{data}' from '{collection}.'")

    async def find(self, collection:  str, query, key: str, max_to_find=50) -> List[dict]:
        """Searches for and returns documents with that query in a collection in this database."""
        try:
            document_list = []
            cursor = self.database[collection].find(query).sort(key)

            for document in await cursor.to_list(max_to_find):
                document_list.append(document)

            return document_list
        except KeyError:
            self.logger.debug(f"Could not find the collection '{collection}'!")
            return None

    async def find_all(self, collection: str, max_to_find=100) -> List[dict] | None:
        """Finds and returns all documents in a collection from this database. This took me a day to make! 😞"""
        try:
            document_list = []
            cursor = self.database[collection].find().sort('_id')

            for document in await cursor.to_list(max_to_find):
                document_list.append(document)

            return document_list
        except KeyError:
            self.logger.debug(f"Could not find the collection '{collection}'!")
            return None

    async def find_one(self, collection: str, query: dict) -> (dict | None):
        """Searches for and returns specific data (document) from a collection in this database."""
        data = await self.database[collection].find_one(query)

        if data is not None:
            self.logger.debug(f"Found '{query}' in '{collection}.'")
            return data
        else:
            self.logger.debug(f"'{query}' was not found in '{collection}.'")
            return None

    async def create_collection(self, collection_name: str, data) -> None:
        await self.database[collection_name].insert_one(data)
        self.logger.debug(f"Database collection '{collection_name}' created.")

    async def get_collection(self, collection: str):
        """Returns cursor of the following collection."""
        return self.database[collection]

    async def delete_collection(self, collection_name: str) -> None:
        await self.database[collection_name].drop()
        self.logger.debug(f"Database collection '{collection_name}' dropped.")

    async def list_collection_names(self) -> List[str]:
        """Returns list of all collection name in this database."""
        return await self.database.list_collection_names()