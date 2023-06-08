from __future__ import annotations
from dataclasses import dataclass, field

from typing import TYPE_CHECKING
from discord_typings import MessageData
from devgoldyutils import DictDataclass

from ... import goldy_bot_logger, LoggerAdapter
from .member import Member

if TYPE_CHECKING:
    from .. import Goldy
    from ..guilds.guild import Guild

logger = LoggerAdapter(goldy_bot_logger, prefix="Message")

@dataclass
class Message(DictDataclass):
    data: MessageData = field(repr=False)
    guild: Guild = field(repr=False)
    goldy:Goldy = field(repr=False)

    # TODO: Add more fields here to data inside the data dict.
    id:str = field(init=False)
    author:Member = field(init=False)
    # TODO: Add more!

    def __post_init__(self):
        super().__post_init__()

        self.logger = logger
        
        self.id = self.get("id")
        self.author = Member(self.get("author"), self.guild, self.goldy)
    
    async def delete(self, reason:str=None) -> Message:
        return await nextcore_utils.delete_msg(self, reason)


from .. import nextcore_utils