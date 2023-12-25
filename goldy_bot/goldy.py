from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from GoldyBot.goldy.database import Database

    from nextcore.http import HTTPClient
    from nextcore.gateway import ShardManager

__all__ = (
    "Goldy",
)

class Goldy():
    """
    The core class that wraps nextcore's shard manager and client. The framework's core class.
    """
    def __init__(
        self, 
        http_client: HTTPClient,
        shard_manager: ShardManager
    ) -> None:
        self.http_client = http_client
        self.shard_manager = shard_manager

        self.__database: Optional[Database] = None

    @property
    def database(self) -> Database:
        """An instance of the framework's mongo database."""
        ...