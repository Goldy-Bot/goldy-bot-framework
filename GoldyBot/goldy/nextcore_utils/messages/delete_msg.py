from __future__ import annotations
from typing import TYPE_CHECKING

from ... import LoggerAdapter, goldy_bot_logger

if TYPE_CHECKING:
    from ...objects import Message

logger = LoggerAdapter(goldy_bot_logger, prefix="delete_msg")

async def delete_msg(message:Message, reason:str=None) -> Message:
    """
    Allows you to delete a message that has been sent.
    
    ------------------

    Parameters
    ----------
    ``message``
        The message object.
    ``reason``
        The reason for why you want to delete this message.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    goldy = message.goldy

    await goldy.http_client.delete_message(
        authentication = goldy.nc_authentication,
        channel_id = message.data["channel_id"],
        message_id = message.data["id"],
        reason = reason
    )

    logger.debug(f"The message '{message.data['content'][:50]}...' at '{message.data['channel_id']}' was deleted.")

    return message