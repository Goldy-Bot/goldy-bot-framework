from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Optional
    from typing_extensions import Self

    from ...typings import GoldySelfT

from ...objects.guild import Guild

__all__ = (
    "Guilds",
)

class Guilds():
    def __init__(self) -> None:
        self._guilds: Dict[str, Guild] = {}

        super().__init__()

    async def get_guild(self: GoldySelfT[Self], guild_id: str) -> Optional[Guild]:
        """Returns a cached guild object of that guild if the bot is in that guild otherwise returns None."""
        guild = self._guilds.get(guild_id)

        if guild is None:
            guild_data = await self.low_level.get_guild_data(guild_id)

            guild = Guild(guild_data, self)

            self._guilds[guild_id] = guild

        return guild