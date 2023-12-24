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
    """The class containing all the framework's core components; pretty much the core of Goldy Bot."""
    def __init__(
        self, 
        http_client: HTTPClient,
        shard_manager: ShardManager
    ) -> None:
        self.database: Optional[Database] = None