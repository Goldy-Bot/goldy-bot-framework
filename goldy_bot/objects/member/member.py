from __future__ import annotations
from typing import TYPE_CHECKING

from discord_typings import UserData

if TYPE_CHECKING:
    from typing import Optional

    from ...goldy import Goldy

from .database import MemberDBWrapper
from ...helpers.dict_helper import DictHelper

__all__ = (
    "Member",
)

class Member(DictHelper[UserData]):
    def __init__(self, data: UserData, goldy: Goldy, guild_id: Optional[str] = None) -> None:
        self.goldy = goldy

        self._guild_id = guild_id

        self.database_wrapper = MemberDBWrapper(goldy.database, self)

        super().__init__(data)

    @property
    async def database(self) -> MemberDBWrapper:
        """Get member's database wrapper."""
        if self.database_wrapper.data is not None:
            await self.database_wrapper.update(self._guild_id)

        return self.database_wrapper