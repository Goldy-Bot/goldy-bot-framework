from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
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
        super().__init__()

    @property
    async def guild(self: PlatterSelfT[Self]) -> Guild:
        # The guild id we pass here to get_guild will always exits 
        # so we can safely infer that it will return a guild object.
        guild_class: Guild = await self.goldy.get_guild(guild_id = self.data["guild_id"])

        return guild_class