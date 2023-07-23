from __future__ import annotations
from typing import overload, List, TYPE_CHECKING, Dict
from discord_typings import MessageReferenceData, InteractionMessageCallbackData, MessageData, InteractionCallbackData, ActionRowData
from discord_typings.resources.channel import MessageBase

from aiohttp import FormData
from nextcore.http import Route
from nextcore.common import json_dumps

from ... import objects
from .... import utils
from ...commands import slash_command
from ...recipes import Recipe

if TYPE_CHECKING:
    from ..files import File
    from ..embeds.embed import Embed

@overload
async def send_msg(
    platter: objects.GoldPlatter, 
    text: str = None, 
    embeds: List[Embed] = None, 
    recipes: List[Recipe] = None, 
    files: List[File] = None, 
    reply: bool = False, 
    delete_after: float = None,
    hide: bool = False,
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
    ``files``
        Files you may upload with this message.
    ``reply``
        Whether goldy bot should liberally reply to the message the command was invoked.
    ``delete_after``
        Deletes the sent message after said amount of seconds.
    ``hide``
        Hides the message in interaction commands and deletes the message after 3 seconds on prefix commands.
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
    files: List[File] = None, 
    delete_after: float = None,
    hide: bool = False,
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
    ``files``
        Files you may upload with this message.
    ``delete_after``
        Deletes the sent message after said amount of seconds.
    ``hide``
        Hides the message in interaction commands and deletes the message after 3 seconds on prefix commands.
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
    files: List[File] = None, 
    delete_after: float = None,
    hide: bool = False,
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
    ``files``
        Files you may upload with this message.
    ``delete_after``
        Deletes the sent message after said amount of seconds.
    ``hide``
        Hides the message in interaction commands and deletes the message after 3 seconds on prefix commands.
    ``**extra``
        Allows you to pass the extra parameters that are missing.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

async def send_msg(
    object: objects.Platter | objects.Member | objects.Channel, 
    text: str = None, 
    embeds: List[Embed] = None, 
    recipes: List[Recipe] = None, 
    files: List[File] = None, 
    reply: bool = False, 
    delete_after: float = None,
    hide: bool = False,
    **extra: MessageData | InteractionCallbackData
) -> objects.Message:
    
    goldy = object.goldy

    form_data = FormData()
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
            recipe.command_platter = object 

            if count / 5 == 0:
                component_count += 1
                components[component_count] = ActionRowData(type=1, components=[])

            components[component_count]["components"].append(recipe)

            count += 1

        payload["components"] = [components[component] for component in components]

    # Adding files to form data.
    if files is not None:
        for file in files:
            form_data.add_field(
                file.name.split(".")[-2], file.contents, filename = file.name
            )

    payload.update(extra)

    message_data: MessageData = None

    if isinstance(object, objects.GoldPlatter):
        platter: objects.GoldPlatter = object

        if isinstance(platter.invokable, (slash_command.SlashCommand, Recipe)):
            # Perform interaction response.
            # ------------------------------
            if hide:
                payload["flags"] = 1 << 6

            # Callback message.
            # ------------------
            if platter._interaction_responded is False:

                form_data.add_field(
                    "payload_json", json_dumps(
                        {
                            "type": 4, 
                            "data": payload
                        }
                    )
                )

                await goldy.http_client.request(
                    Route(
                        "POST", 
                        "/interactions/{interaction_id}/{interaction_token}/callback", 
                        interaction_id = platter.data["id"], 
                        interaction_token = platter.data["token"]
                    ),
                    rate_limit_key = goldy.nc_authentication.rate_limit_key,
                    data = form_data
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

                form_data.add_field(
                    "payload_json", json_dumps(payload)
                )

                r = await goldy.http_client.request(
                    Route(
                        "POST", 
                        "/webhooks/{application_id}/{interaction_token}", 
                        application_id = goldy.application_data["id"], 
                        interaction_token = platter.data["token"]
                    ),
                    rate_limit_key = goldy.nc_authentication.rate_limit_key,
                    data = form_data
                )

                message_data = await r.json()

                platter.logger.debug("Interaction follow up message was sent.")

        else:
            # Perform normal message response.
            # ----------------------------------
            if hide and delete_after is not None:
                delete_after = 3

            if reply:
                payload["message_reference"] = MessageReferenceData(
                    message_id = platter.data["id"],
                    channel_id = platter.data["channel_id"],
                    guild_id = platter.data["guild_id"]
                )

            form_data.add_field(
                "payload_json", json_dumps(payload)
            )

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

        form_data.add_field(
            "payload_json", json_dumps(payload)
        )

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

    # TODO: Find a way to also delete the author's prefix command message.
    if delete_after is not None:
        utils.delay(
            coro = message.delete(f"delete_after was set to {delete_after} seconds"), 
            seconds = delete_after, 
            goldy = goldy
        )

    return message