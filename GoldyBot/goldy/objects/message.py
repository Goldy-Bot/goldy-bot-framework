from __future__ import annotations
from dataclasses import dataclass, field

from typing import TYPE_CHECKING
from discord_typings import MessageData

if TYPE_CHECKING:
    from .. import Goldy

@dataclass
class Message:
    data:MessageData
    goldy:Goldy = field(repr=False)

    # TODO: Add more fields here to data inside the data dict.
    
    async def delete(self, reason:str=None) -> Message:
        return await nextcore_utils.delete_msg(self, reason)


from .. import nextcore_utils