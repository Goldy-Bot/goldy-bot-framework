from __future__ import annotations
from typing import overload
from discord_typings import MessageReferenceData, InteractionMessageCallbackData, MessageData
from discord_typings.resources.channel import MessageBase

from aiohttp import FormData
from nextcore.http import Route
from nextcore.common import json_dumps

from ... import objects

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

async def send_msg(object:objects.GoldPlatter|objects.Member, text:str, reply=False) -> objects.Message:
    message_data:MessageData = None
    goldy = object.goldy
    
    text = str(text)

    # TODO: Add support for member and channel objects.

    if isinstance(object, objects.GoldPlatter):

        if object.type.value == 1:
            # Perform interaction response.
            # ------------------------------

            # Callback message.
            # ------------------
            if object.interaction_responded == False:

                await goldy.http_client.request(
                    Route(
                        "POST", 
                        "/interactions/{interaction_id}/{interaction_token}/callback", 
                        interaction_id = object.data["id"], 
                        interaction_token = object.data["token"]
                    ),
                    rate_limit_key = goldy.nc_authentication.rate_limit_key,
                    json = {
                        "type": 4, 
                        "data": InteractionMessageCallbackData(
                            content = text
                        )
                    }
                )

                object.interaction_responded = True

                # Get and return message data of original interaction response. 
                r = await goldy.http_client.request(
                    Route(
                        "GET", 
                        "/webhooks/{application_id}/{interaction_token}/messages/@original", 
                        application_id = goldy.application_data["id"], 
                        interaction_token = object.data["token"]
                    ),
                    rate_limit_key = goldy.nc_authentication.rate_limit_key
                )

                message_data = await r.json()

                object.command.logger.debug(f"Interaction callback message '{text[:50]}...' was sent.")


            # Follow up message.
            # -------------------
            # Is sent when you want to respond again after sending the original response to an interaction command.
            else:

                r = await goldy.http_client.request(
                    Route(
                        "POST", 
                        "/webhooks/{application_id}/{interaction_token}", 
                        application_id = goldy.application_data["id"], 
                        interaction_token = object.data["token"]
                    ),
                    rate_limit_key = goldy.nc_authentication.rate_limit_key,
                    json = InteractionMessageCallbackData(
                        content = text
                    )
                )

                message_data = await r.json()

                object.command.logger.debug(f"Interaction follow up message '{text[:50]}...' was sent.")

        else:
            # Perform normal message response.
            # ----------------------------------
            payload = MessageBase()

            if reply:
                payload["message_reference"] = MessageReferenceData(
                    message_id = object.data["id"],
                    channel_id = object.data["channel_id"],
                    guild_id = object.data["guild_id"]
                )

            if text is not None:
                payload["content"] = text

            form_data = FormData()
            form_data.add_field("payload_json", json_dumps(payload))

            r = await goldy.http_client.request(
                Route(
                    "POST", 
                    "/channels/{channel_id}/messages", 
                    channel_id = object.data['channel_id']
                ),
                data = form_data,
                rate_limit_key = goldy.nc_authentication.rate_limit_key,
                headers = goldy.nc_authentication.headers,
            )

            message_data = await r.json()

            object.command.logger.debug(f"The message '{text[:50]}...' was sent.")


        return objects.Message(message_data, goldy)
    
    if isinstance(object, objects.Member):
        # TODO: Idk how the fuck to do this.

        ...