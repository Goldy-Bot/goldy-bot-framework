from __future__ import annotations
from typing import TYPE_CHECKING

from nextcore.http import Route

from ... import LoggerAdapter, goldy_bot_logger

if TYPE_CHECKING:
    from ... import objects

logger = LoggerAdapter(goldy_bot_logger, prefix="delete_channel")

async def delete_channel(channel: objects.Channel, reason: str = None) -> objects.Channel:
    """
    Allows you to delete a channel.
    
    ------------------

    Parameters
    ----------
    ``channel``
        The channel object.
    ``reason``
        The reason for why you want to delete this channel.

    Returns
    -------
    :py:meth:`~GoldyBot.goldy.objects.channel.Channel`
        The channel that was deleted.
    """
    goldy = channel.goldy

    headers = goldy.nc_authentication.headers

    if reason is not None:
        headers["X-Audit-Log-Reason"] = reason

    await goldy.http_client.request(
        Route(
            "DELETE",
            "/channels/{channel_id}",
            channel_id = channel.id
        ),
        rate_limit_key = goldy.nc_authentication.rate_limit_key,
        headers = headers,
    )

    logger.debug(f"The channel '{channel.data['name']}' was deleted with reason: {reason}")

    return channel