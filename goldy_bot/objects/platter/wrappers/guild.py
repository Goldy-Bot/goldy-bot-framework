from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from typing_extensions import Self
    from discord_typings import GuildData
    from ....typings.objects import PlatterSelfT

from devgoldyutils import LoggerAdapter

from ...guild.guild import Guild
from ....logger import goldy_bot_logger

__all__ = (
    "GuildWrapper",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "GuildWrapper")

class GuildWrapper():
    def __init__(self: PlatterSelfT[Self]) -> None:
        self.__guild_data: Optional[GuildData] = None

        super().__init__()

    @property
    async def guild(self: PlatterSelfT[Self]) -> Guild:
        if self.__guild_data is None:
            self.__guild_data = await self.goldy.low_level.get_guild(id = self.data["guild_id"])

        return Guild(
            data = self.__guild_data, 
            goldy = self.goldy
        )