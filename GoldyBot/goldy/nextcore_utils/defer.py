from __future__ import annotations
from typing import TYPE_CHECKING

from nextcore.http import Route

from ... import LoggerAdapter, goldy_bot_logger
from ..commands import slash_command
from ..recipes import Recipe

if TYPE_CHECKING:
    from ..objects import GoldPlatter

logger = LoggerAdapter(goldy_bot_logger, prefix="wait")

async def wait(platter: GoldPlatter) -> None:
    """
    Use this to inform Discord and the member that this command will take longer than usual to respond or that a respond is being cooked up. 🍳🍲
    
    ------------------

    Parameters
    -----------
    ``platter``
        The command's platter object.

    Returns
    --------
    ``None``
    """
    goldy = platter.goldy

    if isinstance(platter.invokable, (slash_command.SlashCommand, Recipe)):
        await goldy.http_client.request(
            Route(
                "POST", 
                "/interactions/{interaction_id}/{interaction_token}/callback", 
                interaction_id = platter.data["id"], 
                interaction_token = platter.data["token"]
            ),
            rate_limit_key = goldy.nc_authentication.rate_limit_key,
            json = {
                "type": 5 # Defer
            }
        )

        platter._interaction_responded = True

        logger.debug("We told discord to wait a little longer for this response.")

    else:
        ... # TODO: Add support for prefix commands.

    return None