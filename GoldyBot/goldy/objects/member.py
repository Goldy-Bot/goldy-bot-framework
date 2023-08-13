from __future__ import annotations
from typing import TYPE_CHECKING

from nextcore.http import Route
from devgoldyutils import DictClass, Colours

if TYPE_CHECKING:
    from .. import Goldy
    from ..guilds import Guild
    from discord_typings import UserData, GuildMemberData

from .. import goldy_bot_logger, LoggerAdapter
from ..database.wrappers.member import MemberDBWrapper

logger = LoggerAdapter(goldy_bot_logger, prefix="Member")

class Member(DictClass):
    def __init__(self, data: UserData, guild: Guild, goldy: Goldy) -> None:
        self.data = data
        self.guild = guild
        self.goldy = goldy

        super().__init__(LoggerAdapter(logger, prefix = Colours.GREY.apply(data['username'])))

        self.db_wrapper = MemberDBWrapper(self)
        self.guild_member_data: GuildMemberData = None

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

    @property
    async def member_data(self) -> GuildMemberData:
        if self.guild_member_data is None:
            r = await self.goldy.http_client.request(
                Route(
                    "GET",
                    "/guilds/{guild_id}/members/{user_id}",
                    guild_id = self.guild.id,
                    user_id = self.id
                ),
                rate_limit_key = self.goldy.nc_authentication.rate_limit_key,
                headers = self.goldy.nc_authentication.headers,
            )

            self.guild_member_data = await r.json()

        return self.guild_member_data