from __future__ import annotations

from typing import TYPE_CHECKING
from discord_typings import UserData
from devgoldyutils import DictClass, Colours

from .. import goldy_bot_logger, LoggerAdapter
from ..database.wrappers.member import MemberDBWrapper

if TYPE_CHECKING:
    from .. import Goldy
    from ..guilds import Guild

logger = LoggerAdapter(goldy_bot_logger, prefix="Member")

class Member(DictClass):
    def __init__(self, data: UserData, guild: Guild, goldy: Goldy) -> None:
        self.data = data
        self.guild = guild
        self.goldy = goldy

        super().__init__(LoggerAdapter(logger, prefix=Colours.GREY.apply(data['username'])))

        self.db_wrapper = MemberDBWrapper(self)

    def __repr__(self) -> str:
        return f"{self.name}#{self.discriminator}"

    @property
    def id(self) -> str:
        """Member's id duhhhh."""
        return self.get("id")
    
    @property
    def name(self) -> str:
        """Aliases of username."""
        return self.username

    @property
    def username(self) -> str:
        """Members username. E.g. the ``The Golden Pro`` part of ``The Golden Pro#5675``."""
        return self.get("username")

    @property
    def discriminator(self) -> str:
        """Member's discriminator, their # tag. E.g the ``5675`` part of ``The Golden Pro#5675``."""
        return self.get("discriminator")

    @property
    def avatar_url(self) -> str:
        """The url to the member's profile picture."""
        from .. import nextcore_utils # Avoiding circular import until I find a better way.
        return nextcore_utils.DISCORD_CDN + f"avatars/{self.id}/{self.get('avatar')}.png?size=4096"

    @property
    async def database(self) -> MemberDBWrapper:
        """Get member's database wrapper."""
        if self.db_wrapper.data == {}:
            await self.db_wrapper.update()

        return self.db_wrapper