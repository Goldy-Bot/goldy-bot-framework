from __future__ import annotations
from dataclasses import dataclass, field

from typing import TYPE_CHECKING
from discord_typings import GuildMemberData

if TYPE_CHECKING:
    from .. import Goldy

@dataclass
class Member:
    data:GuildMemberData
    goldy:Goldy = field(repr=False)

    id:str = field(init=False)
    username:str = field(init=False)
    discriminator:str = field(init=False)

    def __post_init__(self):
        self.id = self.data["user"]["id"]
        self.username = self.data["user"]["username"]

        # TODO: Add the rest. Where I left off, 07.03.2023
    

from .. import nextcore_utils