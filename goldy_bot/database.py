from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from motor.core import AgnosticDatabase
    from GoldyBot.goldy.database import DatabaseEnums

from devgoldyutils import LoggerAdapter, Colours
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

from GoldyBot.logging import goldy_bot_logger

__all__ = (
    "Database",
)

# TODO: Move to where the database manager will be initialized.
# MONGODB_URL = config(
#     "MONGODB_URL", 
#     default = "mongodb://localhost:27017", 
#     cast = str
# )

class Database():
    """
    The Goldy Bot 🥞 Pancake class for managing the database.
    """
    def __init__(self, url: str):
        self.url = url

        self._client = AsyncIOMotorClient(url, serverSelectionTimeoutMS = 2000)

        self.logger = LoggerAdapter(goldy_bot_logger, prefix = "DatabaseManager")

    async def _is_connection_ok(self) -> bool:
        try:
            await self._client.server_info()
            self.logger.info("AsyncIOMotorClient " + Colours.GREEN.apply_to_string("Connected!"))

        except ServerSelectionTimeoutError as e:
            self.logger.error(
                f"Couldn't connect to Database! Check if the database URL you entered is correct. Error received from motor >>> {e}"
            )
            return False

        except Exception as e:
            self.logger.error(
                f"Couldn't connect to Database! Error received from motor >>> {e}"
            )
            return False

        return True

    def get_database(self, database_name: DatabaseEnums) -> AgnosticDatabase:
        """Returns a :py:meth:`~motor.core.AgnosticDatabase` database connection."""
        return self._client[database_name.value]