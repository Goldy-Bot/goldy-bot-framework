from __future__ import annotations

from typing import TYPE_CHECKING, List
from discord_typings import UserData
from devgoldyutils import DictClass

from ..database import DatabaseEnums
from ... import goldy_bot_logger, LoggerAdapter
from ..nextcore_utils import DISCORD_CDN
from ..database.wrapper import DatabaseWrapper

if TYPE_CHECKING:
    from .. import Goldy
    from ..guilds import Guild

logger = LoggerAdapter(goldy_bot_logger, prefix="Member")

class Member(DictClass):
    def __init__(self, data: UserData, guild: Guild, goldy: Goldy, db_data: List[dict] = None) -> None:
        self.data = data
        self.guild = guild
        self.goldy = goldy
        
        if db_data is None:
            db_data = []

        self.db_data = db_data

        super().__init__(LoggerAdapter(logger, prefix=data['username']))

    @property
    def id(self) -> str:
        """Member's id duhhhh."""
        return self.get("id")

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
        return DISCORD_CDN + f"avatars/{self.id}/{self.get('avatar')}.png?size=4096"

    @property
    def database(self) -> DatabaseWrapper:
        """The member's database wrapper."""
        return DatabaseWrapper(self, self.logger)