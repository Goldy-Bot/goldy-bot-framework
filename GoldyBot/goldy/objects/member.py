from __future__ import annotations
from dataclasses import dataclass, field
import logging as log

from typing import TYPE_CHECKING, List
from discord_typings import UserData
from devgoldyutils import DictClass

from ..database import GoldyDB, DatabaseEnums
from ... import goldy_bot_logger, LoggerAdapter
from ..nextcore_utils import DISCORD_CDN

if TYPE_CHECKING:
    from .. import Goldy

logger = LoggerAdapter(goldy_bot_logger, prefix="Member")

class Member(DictClass):
    def __init__(self, data: UserData, goldy: Goldy, db_data: List[dict]) -> None:
        self.data = data
        self.goldy = goldy
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
    
    async def update(self) -> None:
        """Updates member's database data by fetching from the database."""
        database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MEMBER_DATA)

        # Let's hope you are not in more than 200 guilds or else this will break! 😫
        self.db_data = await database.find_all(self.id, max_to_find=201)

        return None