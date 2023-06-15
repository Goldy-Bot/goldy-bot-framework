from __future__ import annotations

from typing import TYPE_CHECKING
from devgoldyutils import DictClass, LoggerAdapter, Colours
from abc import abstractmethod, ABC
from .. import DatabaseEnums
from ... import objects

if TYPE_CHECKING:
    from ...guilds import Guild

class DatabaseWrapper(DictClass, ABC):
    """✨ A useful interface class to build a database wrapper for easy of access to database data like member data, guild data and more."""
    def __init__(self, object: objects.Member | Guild) -> None:
        self.goldy = object.goldy
        self.guild = object.guild

        self.data = {}

        super().__init__(
            LoggerAdapter(object.logger, prefix=Colours.PINK_GREY.apply("Database Wrapper"))
        )

    @abstractmethod
    async def push(self, type: DatabaseEnums | str, data: dict) -> None:
        """Push new data directly to the database."""
        ...

    @abstractmethod
    async def update(self) -> None:
        """Update the wrapper with the greatest and latest data from the database."""
        ...

        """
        if isinstance(self.goldy, Guild):
            database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MAIN)

            #self.data = await database.find_one("guild_configs", query = {"_id": self.id})

            # TODO: Move guild database stuff to this wrapper.
        """