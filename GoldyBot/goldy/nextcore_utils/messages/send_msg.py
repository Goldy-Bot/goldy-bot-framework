from __future__ import annotations
from typing import overload
from discord_typings import MessageReferenceData, InteractionMessageCallbackData

from nextcore.http import Route, errors as nc_errors

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
        # Perform interaction response.
        # ------------------------------

        # Callback message.
        if platter.interaction_responded == False:

            route = Route(
                "POST", 
                "/interactions/{interaction_id}/{interaction_token}/callback", 
                interaction_id = platter.data["id"], 
                interaction_token = platter.data["token"]
            )

            await goldy.http_client._request(
                route,
                rate_limit_key = goldy.nc_authentication.rate_limit_key,
                json = {
                    "type": 4, 
                    "data": InteractionMessageCallbackData(
                        content = text
                    )
                }
            )

            platter.interaction_responded = True

            platter.command.logger.debug(f"Interaction callback message '{text[:50]}...' sent.")

        # Follow up message.
        else:

            route = Route(
                "POST", 
                "/webhooks/{application_id}/{interaction_token}", 
                application_id = goldy.application_data["id"], 
                interaction_token = platter.data["token"]
            )

            test = await goldy.http_client._request(
                route,
                rate_limit_key = goldy.nc_authentication.rate_limit_key,
                json = {
                    "type": 4, 
                    "data": InteractionMessageCallbackData(
                        content = text
                    )
                }
            )

            # TODO: Where I left off last night.

            print(await test.json())

            platter.command.logger.debug(f"Interaction follow up message '{text[:50]}...' sent.")

        # Get message data of interaction response.
        # -------------------------------------------
        route = Route(
            "GET", 
            "/webhooks/{application_id}/{interaction_token}/messages/@original", 
            application_id = goldy.application_data["id"], 
            interaction_token = platter.data["token"]
        )

        r = await goldy.http_client._request(
            route,
            rate_limit_key = goldy.nc_authentication.rate_limit_key
        )

        message_data = await r.json()

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