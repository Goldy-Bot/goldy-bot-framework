from __future__ import annotations
from typing import TYPE_CHECKING
from discord_typings import GuildData

from nextcore.http import Route

from ... import LoggerAdapter, goldy_bot_logger

if TYPE_CHECKING:
    from ... import Goldy

logger = LoggerAdapter(goldy_bot_logger, prefix="get_guild_data")

async def get_guild_data(guild_id: str, goldy: Goldy) -> GuildData:
    """
    Returns the guild's discord data.

    ------------------

    Parameters
    ----------
    ``guild_id``
        The id of the guild.

    Returns
    -------
    :py:meth:`~discord_typings.GuildData`
        A dictionary of guild data.
    """

    headers = goldy.nc_authentication.headers

    r = await goldy.http_client.request(
        Route(
            "GET",
            "/guilds/{guild_id}",
            guild_id = str(guild_id)
        ),
        rate_limit_key = goldy.nc_authentication.rate_limit_key,
        headers = headers,
    )

    guild_data: GuildData = await r.json()

    logger.debug(f"Grabbed guild data for the guild with id '{guild_id}'.")

    return guild_data