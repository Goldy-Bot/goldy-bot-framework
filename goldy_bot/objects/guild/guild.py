from __future__ import annotations
from typing import TYPE_CHECKING

from discord_typings import GuildData

if TYPE_CHECKING:
    from ...goldy import Goldy

from .database import GuildDBWrapper
from ...helpers.dict_helper import DictHelper

__all__ = (
    "Guild",
)

class Guild(DictHelper[GuildData]):
    def __init__(self, data: GuildData, goldy: Goldy) -> None:
        self.goldy = goldy

        self.database_wrapper = GuildDBWrapper(goldy.database, self)

        super().__init__(data)

    @property
    async def database(self) -> GuildDBWrapper[dict]:
        """Get guild's database wrapper."""
        if self.database_wrapper.data is None:
            await self.database_wrapper.update()

        return self.database_wrapper