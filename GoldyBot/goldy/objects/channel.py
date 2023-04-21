from __future__ import annotations
from dataclasses import dataclass, field

from typing import TYPE_CHECKING
from discord_typings import ChannelData
from devgoldyutils import DictDataclass

from ... import goldy_bot_logger, LoggerAdapter

if TYPE_CHECKING:
    from .. import Goldy

logger = LoggerAdapter(goldy_bot_logger, prefix="Channel")

@dataclass
class Channel(DictDataclass):
    data: ChannelData = field(repr=False)
    goldy: Goldy = field(repr=False)

    id:str = field(init=False)
    # TODO: Add more!

    def __post_init__(self):
        super().__post_init__()
        
        self.logger = logger
        
        self.id = self.get("id")
    
    async def delete(self, reason:str=None) -> Channel:
        return await nextcore_utils.delete_channel(self, reason)


from .. import nextcore_utils