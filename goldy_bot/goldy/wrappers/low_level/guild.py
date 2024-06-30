from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from discord_typings import GuildData

    from ....typings import LowLevelSelfT

from nextcore.http import Route

__all__ = (
    "Guild",
)

class Guild():
    def __init__(self) -> None:
        super().__init__()

    async def get_guild(self: LowLevelSelfT[Self], id: str, **kwargs) -> GuildData:
        self.logger.debug(f"Requesting data of guild '{id}'...")

        r = await self.goldy.client.request(
            Route(
                "GET", 
                "/guilds/{guild_id}", 
                guild_id = id
            ), 
            **self.goldy.key_and_headers, 
            **kwargs
        )

        data = await r.json()
        return data