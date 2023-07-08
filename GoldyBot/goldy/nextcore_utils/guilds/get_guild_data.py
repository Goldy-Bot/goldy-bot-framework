from __future__ import annotations
from typing import TYPE_CHECKING
from discord_typings import GuildData

from nextcore.http import Route

from ... import LoggerAdapter, goldy_bot_logger

if TYPE_CHECKING:
    from ...guilds import Guild

logger = LoggerAdapter(goldy_bot_logger, prefix="get_channels")

async def get_guild_data(guild: Guild) -> GuildData:
    """
    Returns the guild's discord data.

    ------------------

    Parameters
    ----------
    ``guild``
        The guild object.

    Returns
    -------
    :py:meth:`~discord_typings.GuildData`
        A dictionary of guild data.
    """
    goldy = guild.goldy

    headers = goldy.nc_authentication.headers

    r = await goldy.http_client.request(
        Route(
            "GET",
            "/guilds/{guild_id}",
            guild_id = guild.id
        ),
        rate_limit_key = goldy.nc_authentication.rate_limit_key,
        headers = headers,
    )

    guild_data: GuildData = await r.json()

    logger.debug(f"Grabbed guild data for the guild '{guild.code_name}'.")

    return guild_data