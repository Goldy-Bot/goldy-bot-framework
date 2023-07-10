from __future__ import annotations

from typing import TYPE_CHECKING

import logging
from devgoldyutils import DictClass, LoggerAdapter, Colours
from abc import abstractmethod, ABC
from .. import DatabaseEnums

if TYPE_CHECKING:
    from ... import Goldy
    from ...guilds import Guild

class DatabaseWrapper(DictClass, ABC):
    """✨ A useful interface class to build a database wrapper for easy of access to database data like member data, guild data and more."""
    def __init__(self, goldy: Goldy, logger: logging.Logger) -> None:
        self.goldy = goldy

        self.data = {}

        super().__init__(
            LoggerAdapter(logger, prefix=Colours.PINK_GREY.apply("Database Wrapper"))
        )

    @abstractmethod
    async def push(self, type: DatabaseEnums | str, data: dict) -> None:
        """Push new data directly to the database."""
        ...

    @abstractmethod
    async def update(self) -> None:
        """Update the wrapper with the greatest and latest data from the database."""
        ...

        """ # TODO: Remove this when guild database wrapper is implemented.
        if isinstance(self.goldy, Guild):
            database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MAIN)

            #self.data = await database.find_one("guild_configs", query = {"_id": self.id})

            # TODO: Move guild database stuff to this wrapper.
        """