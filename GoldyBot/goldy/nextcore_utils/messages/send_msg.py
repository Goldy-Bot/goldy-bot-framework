from __future__ import annotations
from typing import overload
from discord_typings import MessageReferenceData

from ... import objects
from .... import errors

# TODO: Add more options to allow using channel instead of platter.

@overload
async def send_msg(platter:objects.GoldPlatter, test:str, reply=False): # Work in progress...
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
        Whether goldy bot should liberally reply to the message the command was invoked..

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

@overload
async def send_msg(channel, text:str): # TODO: Add type to channel when channel object is available.
    """
    Allows you to create and send a message to this specific channel.
    
    ------------------

    Parameters
    ----------
    ``channel``
        The channel the message should be sent to.
    ``text``
        The content of the message.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

@overload
async def send_msg(member:objects.Member, text:str):
    """
    Allows you to create and send a message to this member's dms.
    
    ------------------

    Parameters
    ----------
    ``member``
        The member the message should be sent to.
    ``text``
        The content of the message.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

async def send_msg(platter:objects.GoldPlatter, text:str, reply=False) -> objects.Message:
    message_data = None
    message_reference_data = None
    goldy = platter.goldy

    # TODO: Add support for member and channel objects.

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