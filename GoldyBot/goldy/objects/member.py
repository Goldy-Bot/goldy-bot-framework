from __future__ import annotations
from dataclasses import dataclass, field

from typing import TYPE_CHECKING
from discord_typings import GuildMemberData
from ...urls import USER_AVATAR

if TYPE_CHECKING:
    from .. import Goldy

@dataclass
class Member:
    data:GuildMemberData
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
        self.id = self.data["user"]["id"]
        self.username = self.data["user"]["username"]
        self.discriminator = self.data["user"]["discriminator"]
        self.avatar_url = USER_AVATAR.format(self.id, self.data["user"]["avatar"])

        # TODO: Add the rest. Where I left off, 07.03.2023
    

from .. import nextcore_utils