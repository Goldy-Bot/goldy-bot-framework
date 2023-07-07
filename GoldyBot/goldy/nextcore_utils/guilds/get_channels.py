from __future__ import annotations
from typing import TYPE_CHECKING, List
from discord_typings import ChannelData

from nextcore.http import Route

from ... import LoggerAdapter, goldy_bot_logger, objects

if TYPE_CHECKING:
    from ...guilds import Guild

logger = LoggerAdapter(goldy_bot_logger, prefix="get_channels")

async def get_channels(guild: Guild) -> List[objects.Channel]:
    """
    Returns a list of channels in that guild.

    ------------------

    Parameters
    ----------
    ``guild``
        The guild object.

    Returns
    -------
    List[:py:meth:`~GoldyBot.goldy.objects.channel.Channel`]
        A list of channels that are in this guild.
    """
    goldy = guild.goldy

    headers = goldy.nc_authentication.headers

    r = await goldy.http_client.request(
        Route(
            "GET",
            "/guilds/{guild_id}/channels",
            guild_id = guild.id
        ),
        rate_limit_key = goldy.nc_authentication.rate_limit_key,
        headers = headers,
    )

    guild_channels: List[ChannelData] = await r.json()

    logger.debug(f"Grabbed all channels from the guild '{guild.code_name}'.")

    return [objects.Channel(channel_data, guild, goldy) for channel_data in guild_channels]