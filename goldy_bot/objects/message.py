from __future__ import annotations
from typing import TYPE_CHECKING

from discord_typings import MessageData

if TYPE_CHECKING:
    from typing import Optional

    from ..goldy import Goldy

from ..helper import DictHelper

__all__ = (
    "Message",
)

class Message(DictHelper[MessageData]):
    def __init__(self, data: MessageData, goldy: Goldy) -> None:
        self.goldy = goldy

        super().__init__(data)

    async def delete(self, reason: Optional[str] = None) -> Message:
        await self.goldy.delete_message(
            channel_id = self.data["channel_id"], 
            message_id = self.data["id"], 
            reason = reason
        )