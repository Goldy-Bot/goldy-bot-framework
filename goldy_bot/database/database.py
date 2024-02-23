from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional

    from .enums import DatabaseEnums
    from motor.core import AgnosticDatabase, AgnosticCollection

from devgoldyutils import LoggerAdapter, Colours
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

from GoldyBot import utils as legacy_utils

from ..logger import goldy_bot_logger

__all__ = (
    "Database",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "Database")

class Database():
    """
    The Goldy Bot 🥞 Pancake class for managing the database.
    """
    def __init__(self, url: str):
        self.url = url

        self._client = AsyncIOMotorClient(url, serverSelectionTimeoutMS = 2000)

    async def _is_connection_ok(self) -> bool:
        try:
            await self._client.server_info()
            logger.info("AsyncIOMotorClient " + Colours.GREEN.apply_to_string("Connected!"))

        except ServerSelectionTimeoutError as e:
            logger.error(
                f"Couldn't connect to Database! Check if the database URL you entered is correct. Error received from motor >>> {e}"
            )
            return False

        except Exception as e:
            logger.error(
                f"Couldn't connect to Database! Error received from motor >>> {e}"
            )
            return False

        return True

    def get_database(self, database_name: DatabaseEnums) -> AgnosticDatabase:
        """Returns a :py:meth:`~motor.core.AgnosticDatabase` database connection."""
        return self._client[database_name.value]

    @classmethod
    async def edit(cls, collection: AgnosticCollection, query, data: dict, overwrite: bool = False) -> dict:
        """Finds and edits a document in a collection with the data provided."""
        if overwrite:
            await collection.update_one(query, {"$set": data}, upsert = True)
        else:
            document_data = await collection.find_one(query)
            data = legacy_utils.update_dict(document_data, data) if document_data is not None else data # NOTE: I don't remember why I did this in legacy again.
            await collection.update_one(query, {"$set": data}, upsert = True)

        logger.debug(f"Edited '{query}' with '{data}.'")
        return await collection.find_one(query)

    @classmethod
    async def find(self, collection: AgnosticCollection, query, key: str, max_to_find = 50) -> Optional[List[dict]]:
        """Searches for and returns documents with that query in a collection in this database."""
        try:
            document_list = []
            cursor = collection.find(query).sort(key)

            for document in await cursor.to_list(max_to_find):
                document_list.append(document)

            return document_list
        except KeyError:
            logger.debug(f"Could not find the collection '{collection}'!")
            return None