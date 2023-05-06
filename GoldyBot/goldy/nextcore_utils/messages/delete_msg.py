from __future__ import annotations
from typing import TYPE_CHECKING

from nextcore.http import Route

from ... import LoggerAdapter, goldy_bot_logger

if TYPE_CHECKING:
    from ...objects import Message

logger = LoggerAdapter(goldy_bot_logger, prefix="delete_msg")

async def delete_msg(message: Message, reason: str=None) -> Message:
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
        The message that we deleted.
    """
    goldy = message.goldy

    headers = goldy.nc_authentication.headers

    if reason is not None:
        headers["X-Audit-Log-Reason"] = reason

    await goldy.http_client.request(
        Route(
            "DELETE", 
            "/channels/{channel_id}/messages/{message_id}", 
            channel_id = message.data["channel_id"], 
            message_id = message.data["id"]
        ),
        rate_limit_key = goldy.nc_authentication.rate_limit_key,
        headers = headers
    )

    logger.debug(f"A message in the channel '{message.data['channel_id']}' was deleted with reason: {reason}")

    return message