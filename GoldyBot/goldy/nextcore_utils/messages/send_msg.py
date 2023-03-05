from __future__ import annotations
from typing import TYPE_CHECKING, overload
from discord_typings import MessageReferenceData

from ...objects import Message
from ....errors import GoldyBotError

if TYPE_CHECKING:
    from ...objects import GoldPlatter

async def send_msg(platter:GoldPlatter, text:str, reply=False) -> Message:
    """
    Allows you to create and send a message to the channel the command was invoked as a form of reply.
    
    ------------------

    Parameters
    ----------
    ``platter``
        The gold platter from the command.
    ``text``
        The content of the message.
    ``reply``
        Whether goldy bot should reply to the command or not.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    data = None
    message_reference_data = None
    goldy = platter.goldy

    if platter.type.value == 1:
        # TODO: Add support for slash once application command responding is functioning in nextcore.
        raise GoldyBotError("send_msg not supported yet for slash commands! Will be supported soon...", platter.command.logger)
    
    else:
        if reply:
            message_reference_data = MessageReferenceData(
                message_id = platter.data["id"],
                channel_id = platter.data["channel_id"],
                guild_id = platter.data["guild_id"]
            )

        data = await goldy.http_client.create_message(
            authentication = goldy.nc_authentication,
            channel_id = platter.data['channel_id'],
            content = text,
            message_reference = (lambda x: x if not None else None)(message_reference_data)
        )

        platter.command.logger.debug(f"The message '{text[:50]}...' was sent.")

    return Message(data)