from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from typing_extensions import Self

    from ....typings import GoldySelfT

from nextcore.http import Route
from devgoldyutils import LoggerAdapter

from ....logger import goldy_bot_logger

__all__ = (
    "Channel",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "Channel")

class Channel():
    def __init__(self) -> None:
        super().__init__()

    # TODO: Upgrade this to be able to bulk delete multiple messages.
    async def delete_message(
        self: GoldySelfT[Self], 
        channel_id: str, 
        message_id: str, 
        reason: Optional[str] = None
    ) -> None: 
        """Deletes a single message."""
        logger.debug(
            f"Deleting message '{message_id}' in channel '{channel_id}'..." + "" if reason is None else f" (Reason: {reason})"
        )

        await self.client.request(
            Route(
                "DELETE", 
                "/channels/{channel_id}/messages/{message_id}", 
                channel_id = channel_id, 
                message_id = message_id
            ),
            rate_limit_key = self.key_and_headers["rate_limit_key"]
        )