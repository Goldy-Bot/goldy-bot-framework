from __future__ import annotations
from typing import TYPE_CHECKING

from nextcore.http import Route
from discord_typings import ChannelData

from ... import LoggerAdapter, goldy_bot_logger, objects

if TYPE_CHECKING:
    from ... import Goldy

logger = LoggerAdapter(goldy_bot_logger, prefix="delete_channel")

async def get_channel(channel_id: str | int, goldy: Goldy) -> objects.Channel:
    """
    Allows you to get a channel by id.

    ------------------

    Parameters
    ----------
    ``channel_id``
        The id of the channel.

    Returns
    -------
    :py:meth:`~GoldyBot.goldy.objects.channel.Channel`
        The channel object.
    """
    headers = goldy.nc_authentication.headers

    r = await goldy.http_client.request(
        Route(
            "GET",
            "/channels/{channel_id}",
            channel_id = str(channel_id)
        ),
        rate_limit_key = goldy.nc_authentication.rate_limit_key,
        headers = headers,
    )

    data: ChannelData  = await r.json()

    logger.debug(f"We got the channel '{data['name']}'.")

    return objects.Channel(data, goldy.guild_manager.get_guild(data["guild_id"]), goldy)