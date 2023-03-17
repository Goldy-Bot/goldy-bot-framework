from __future__ import annotations
from dataclasses import dataclass, field

from typing import TYPE_CHECKING
from discord_typings import UserData
from devgoldyutils import DictDataclass

from ... import goldy_bot_logger, LoggerAdapter
from ..nextcore_utils.urls import USER_AVATAR

if TYPE_CHECKING:
    from .. import Goldy

logger = LoggerAdapter(goldy_bot_logger, prefix="Member")

@dataclass
class Member(DictDataclass):
    data:UserData
    goldy:Goldy = field(repr=False)

    id:str = field(init=False)
    """Member's id duhhhh."""
    username:str = field(init=False)
    """Members username. E.g. the ``The Golden Pro`` part of ``The Golden Pro#5675``."""
    discriminator:str = field(init=False)
    """Member's discriminator, their # tag. E.g the ``5675`` part of ``The Golden Pro#5675``."""
    avatar_url:str = field(init=False)
    """The url to the member's profile picture."""

    def __post_init__(self):
        self.logger = logger

        self.id = self.get("id")
        self.username = self.get("username")
        self.discriminator = self.get("discriminator")
        self.avatar_url = USER_AVATAR.format(
            user_id = self.id, 
            user_avatar_hash = self.get("avatar")
        )