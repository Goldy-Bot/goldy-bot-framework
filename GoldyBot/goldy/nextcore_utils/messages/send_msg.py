from __future__ import annotations
from discord_typings import MessageReferenceData

from ... import objects
from .... import errors

async def send_msg(platter:objects.GoldPlatter, text:str, reply=False) -> objects.Message:
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
    message_data = None
    message_reference_data = None
    goldy = platter.goldy

    if platter.type.value == 1:
        # TODO: Add support for slash once application command responding is functioning in nextcore.
        raise errors.NotSupportedYetForSlash("send_msg", platter.command.logger)
    
    else:
        if reply:
            message_reference_data = MessageReferenceData(
                message_id = platter.data["id"],
                channel_id = platter.data["channel_id"],
                guild_id = platter.data["guild_id"]
            )

        message_data = await goldy.http_client.create_message(
            authentication = goldy.nc_authentication,
            channel_id = platter.data['channel_id'],
            content = text,
            message_reference = (lambda x: x if not None else None)(message_reference_data)
        )

        platter.command.logger.debug(f"The message '{text[:50]}...' was sent.")

    return objects.Message(message_data, goldy)