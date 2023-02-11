from __future__ import annotations

from ... import LoggerAdapter

from typing import List

class GoldyDB():
    """A class representing a singular goldy bot database in mongoDB."""
    def __init__(self, core_database, code_name:str) -> None:
        self.client = core_database.client
        self.database = self.client[code_name]
        
        self.logger = LoggerAdapter(core_database.logger, code_name)

    async def insert(self, collection:str, data) -> bool:
        """Inserts the data provided into a collection in this database."""
        await self.database[collection].insert_one(data)
        self.logger.debug(f"Inserted '{data}' into '{collection}.'")
        return True

    async def edit(self, collection:str, query, data:dict) -> bool:
        """Finds and edits a document in this database and collection with the data provided."""
        await self.database[collection].update_one(query, {"$set": data})
        self.logger.debug(f"Edited '{query}' into '{data}.'")
        return True

    async def remove(self, collection:str, data) -> bool:
        """Finds and deletes a copy of this data from a collection in this database."""
        await self.database[collection].delete_one(data)
        self.logger.debug(f"Deleted '{data}' from '{collection}.'")
        return True

    async def find(self, collection:str, query, key:str, max_to_find=50) -> List[dict]:
        """Searches for and returns documents with that query in a collection in this database."""
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
        """Finds and returns all documents in a collection from this database. This took me a day to make! 😞"""
        try:
            document_list = []
            cursor = self.database[collection].find().sort('_id')

            for document in await cursor.to_list(max_to_find):
                document_list.append(document)

            return document_list
        except KeyError as e:
            self.logger.debug(f"Could not find the collection '{collection}'!")
            return None

    async def find_one(self, collection:str, query:dict) -> (dict | None):
        """Searches for and returns specific data from a collection in this database."""
        data = await self.database[collection].find_one(query)

        if not data is None:
            self.logger.debug(f"Found '{query}' in '{collection}.'")
            return data
        else:
            self.logger.debug(f"'{query}' was not found in '{collection}.'")
            return None

    async def create_collection(self, collection_name:str, data) -> bool:
        await self.database[collection_name].insert_one(data)
        self.logger.debug(f"Database collection '{collection_name}' created.")
        return True

    async def get_collection(self, collection:str):
        """Returns cursor of the following collection."""
        return self.database[collection]

    async def delete_collection(self, collection_name:str) -> bool:
        await self.database[collection_name].drop()
        self.logger.debug(f"Database collection '{collection_name}' dropped.")
        return True

    async def list_collection_names(self) -> List[str]:
        """Returns list of all collection name in this database."""
        return await self.database.list_collection_names()