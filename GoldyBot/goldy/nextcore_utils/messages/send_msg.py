from __future__ import annotations
from typing import overload, List, TYPE_CHECKING, Dict
from discord_typings import MessageReferenceData, InteractionMessageCallbackData, MessageData, InteractionCallbackData, ActionRowData
from discord_typings.resources.channel import MessageBase

from aiohttp import FormData
from nextcore.http import Route
from nextcore.common import json_dumps

from ... import objects, utils

if TYPE_CHECKING:
    from ..components import Recipe
    from ..embeds.embed import Embed

# TODO: Add more options to allow using channel instead of platter.

@overload
async def send_msg(
    platter: objects.GoldPlatter, 
    text: str = None, 
    embeds: List[Embed] = None, 
    recipes: List[Recipe] = None, 
    reply: bool = False, 
    **extra: MessageData | InteractionCallbackData
) -> objects.Message: # Work in progress...
    """
    Allows you to create and send a message to the channel the command was invoked from as a form of reply.
    
    ------------------

    Parameters
    ----------
    ``platter``
        The gold platter from the command.
    ``text``
        The content of the message.
    ``embeds``
        Embeds to include in the message.
    ``recipes``
        Components to include in the message.
    ``reply``
        Whether goldy bot should liberally reply to the message the command was invoked.
    ``**extra``
        Allows you to pass the extra parameters that are missing.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

@overload
async def send_msg(
    channel: objects.Channel, 
    text: str = None,
    embeds: List[Embed] = None, 
    recipes: List[Recipe] = None, 
    **extra: MessageData | InteractionCallbackData
) -> objects.Message:
    """
    Allows you to create and send a message to this specific channel.
    
    ------------------

    Parameters
    ----------
    ``channel``
        The channel the message should be sent to.
    ``text``
        The content of the message.
    ``embeds``
        Embeds to include in the message.
    ``recipes``
        Components to include in the message.
    ``**extra``
        Allows you to pass the extra parameters that are missing.
        
    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

@overload
async def send_msg(
    member: objects.Member, 
    text: str = None, 
    embeds: List[Embed] = None, 
    recipes: List[Recipe] = None, 
    **extra: MessageData | InteractionCallbackData
) -> objects.Message:
    """
    Allows you to create and send a message to this member's dms.
    
    ------------------

    Parameters
    ----------
    ``member``
        The member the message should be sent to.
    ``text``
        The content of the message.
    ``embeds``
        Embeds to include in the message.
    ``recipes``
        Components to include in the message.
    ``**extra``
        Allows you to pass the extra parameters that are missing.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

async def send_msg(
    object: objects.GoldPlatter | objects.Member | objects.Channel, 
    text: str = None, 
    embeds: List[Embed] = None, 
    recipes: List[Recipe] = None, 
    reply: bool = False, 
    delete_after: float = None,
    **extra: MessageData | InteractionCallbackData
) -> objects.Message:
    
    goldy = object.goldy
    
    payload: MessageBase | InteractionMessageCallbackData = {}

    if text is not None:
        payload["content"] = str(text)

    if embeds is not None:
        payload["embeds"] = embeds

    if recipes is not None:
        components: Dict[int, ActionRowData] = {}

        count = 0
        component_count = 0
        for recipe in recipes:
            # Recipes need the command platter object for when checking if it was the author who invoked a recipe.
            recipe.cmd_platter = object 

            if count / 5 == 0:
                component_count += 1
                components[component_count] = ActionRowData(type=1, components=[])

            components[component_count]["components"].append(recipe)
            
            count += 1

        payload["components"] = [components[component] for component in components]

    payload.update(extra)


    message_data: MessageData = None

    if isinstance(object, objects.GoldPlatter):
        platter: objects.GoldPlatter = object

        if platter.type.value == 1:
            # Perform interaction response.
            # ------------------------------

            # Callback message.
            # ------------------
            if platter._interaction_responded is False:

                await goldy.http_client.request(
                    Route(
                        "POST", 
                        "/interactions/{interaction_id}/{interaction_token}/callback", 
                        interaction_id = platter.data["id"], 
                        interaction_token = platter.data["token"]
                    ),
                    rate_limit_key = goldy.nc_authentication.rate_limit_key,
                    json = {
                        "type": 4, 
                        "data": payload
                    }
                )

                platter._interaction_responded = True

                # Get and return message data of original interaction response. 
                r = await goldy.http_client.request(
                    Route(
                        "GET", 
                        "/webhooks/{application_id}/{interaction_token}/messages/@original", 
                        application_id = goldy.application_data["id"], 
                        interaction_token = platter.data["token"]
                    ),
                    rate_limit_key = goldy.nc_authentication.rate_limit_key
                )

                message_data = await r.json()

                platter.logger.debug("Interaction callback message was sent.")


            # Follow up message.
            # -------------------
            # Is sent when you want to respond again after sending the original response to an interaction command.
            else:

                r = await goldy.http_client.request(
                    Route(
                        "POST", 
                        "/webhooks/{application_id}/{interaction_token}", 
                        application_id = goldy.application_data["id"], 
                        interaction_token = platter.data["token"]
                    ),
                    rate_limit_key = goldy.nc_authentication.rate_limit_key,
                    json = payload
                )

                message_data = await r.json()

                platter.logger.debug("Interaction follow up message was sent.")

        else:
            # Perform normal message response.
            # ----------------------------------

            if reply:
                payload["message_reference"] = MessageReferenceData(
                    message_id = platter.data["id"],
                    channel_id = platter.data["channel_id"],
                    guild_id = platter.data["guild_id"]
                )

            form_data = FormData()
            form_data.add_field("payload_json", json_dumps(payload))

            r = await goldy.http_client.request(
                Route(
                    "POST", 
                    "/channels/{channel_id}/messages", 
                    channel_id = platter.data['channel_id']
                ),
                data = form_data,
                rate_limit_key = goldy.nc_authentication.rate_limit_key,
                headers = goldy.nc_authentication.headers,
            )

            message_data = await r.json()

            platter.logger.debug("Message was sent.")


    # If object is a channel object just send the message in the channel.
    if isinstance(object, objects.Channel):
        channel: objects.Channel = object

        form_data = FormData()
        form_data.add_field("payload_json", json_dumps(payload))

        r = await goldy.http_client.request(
            Route(
                "POST", 
                "/channels/{channel_id}/messages", 
                channel_id = channel.id
            ),
            data = form_data,
            rate_limit_key = goldy.nc_authentication.rate_limit_key,
            headers = goldy.nc_authentication.headers,
        )

        message_data = await r.json()

        channel.logger.debug(f"Message was sent in channel '{channel.data['name']}'.")

    message = objects.Message(message_data, object.guild, goldy)

    if delete_after is not None:
        utils.delay(
            coro = message.delete(f"delete_after was set to {delete_after} seconds"), 
            seconds = delete_after, 
            goldy = goldy
        )

    return message