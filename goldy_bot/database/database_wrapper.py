from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Optional
from typing_extensions import TypeVar

if TYPE_CHECKING:
    from typing import Any

    from .database import Database

    T = TypeVar("T", default = None)

DatabaseWrapperDataT = TypeVar("DatabaseWrapperDataT", default = Optional[dict])

from abc import abstractmethod, ABC

__all__ = (
    "DatabaseWrapper",
)

class DatabaseWrapper(Generic[DatabaseWrapperDataT], ABC):
    """✨ A useful interface class to build a database wrapper for easy of access to database data like member data, guild data and more."""
    def __init__(self, database: Database) -> None:
        self.database = database

        self.data: DatabaseWrapperDataT = None

        super().__init__()

    @abstractmethod
    async def push(self, data: dict) -> None:
        """Push new data directly to the database."""
        ...

    @abstractmethod
    async def update(self) -> None:
        """Update the wrapper with the greatest and latest data from the database."""
        ...

    def get(self, key: str, default: T = None) -> Any | T:
        """Retrieve data."""
        if self.data is None:
            return default

        return self.data.get(key, default)