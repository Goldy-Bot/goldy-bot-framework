from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List, Dict

    from discord_typings import (
        MessageData,
        ActionRowData,
        InteractionData, 
        InteractionMessageCallbackData
    )

    from GoldyBot import Embed, Recipe, File

    from ...goldy import Goldy

from aiohttp import FormData
from nextcore.http import Route
from nextcore.common import json_dumps
from devgoldyutils import LoggerAdapter

from .wrapper import PlatterWrapper
from ...logger import goldy_bot_logger

__all__ = (
    "MessagingWrapper",
)

class MessagingWrapper(PlatterWrapper):
    def __init__(self, data: InteractionData, goldy: Goldy) -> None:
        self._interaction_responded = False

        self.logger = LoggerAdapter(goldy_bot_logger, prefix = "MessagingWrapper")

        super().__init__(data, goldy)

    async def send_message(
        self,
        text: Optional[str] = None, 
        embeds: Optional[List[Embed]] = None, 
        recipes: Optional[List[Recipe]] = None, 
        files: Optional[List[File]] = None, 
        delete_after: Optional[float] = None,
        hide: bool = False,
        **kwargs
    ) -> None: # TODO: Make this return a message object.

        form_data = FormData()
        payload: InteractionMessageCallbackData = {}

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

        payload.update(kwargs)

        message_data: MessageData = None

        if hide: # shows the message only to the user
            payload["flags"] = 1 << 6

        # Callback message.
        # ------------------
        if self._interaction_responded is False:

            form_data.add_field(
                "payload_json", json_dumps(
                    {
                        "type": 4, 
                        "data": payload
                    }
                )
            )

            await self.goldy.http_client.request(
                Route(
                    "POST", 
                    "/interactions/{interaction_id}/{interaction_token}/callback", 
                    interaction_id = self.data["id"], 
                    interaction_token = self.data["token"]
                ),
                rate_limit_key = self.goldy.shard_manager.authentication.rate_limit_key,
                data = form_data
            )

            self._interaction_responded = True

            # Get and return message data of original interaction response. 
            r = await self.goldy.http_client.request(
                Route(
                    "GET", 
                    "/webhooks/{application_id}/{interaction_token}/messages/@original", 
                    application_id = self.goldy.application_data["id"], 
                    interaction_token = self.data["token"]
                ),
                rate_limit_key = self.goldy.shard_manager.authentication.rate_limit_key
            )

            message_data = await r.json()

            self.logger.debug("Interaction callback message was sent.")

        # Follow up message.
        # -------------------
        # Is sent when you want to respond again after sending the original response to an interaction command.
        else:

            form_data.add_field(
                "payload_json", json_dumps(payload)
            )

            r = await self.goldy.http_client.request(
                Route(
                    "POST", 
                    "/webhooks/{application_id}/{interaction_token}", 
                    application_id = self.goldy.application_data["id"], 
                    interaction_token = self.data["token"]
                ),
                rate_limit_key = self.goldy.shard_manager.authentication.rate_limit_key,
                data = form_data
            )

            message_data = await r.json()

            self.logger.debug("Interaction follow up message was sent.")

        """
        message = objects.Message(message_data, object.guild, goldy)

        # TODO: Find a way to also delete the author's prefix command message.
        if delete_after is not None:
            utils.delay(
                coro = message.delete(f"delete_after was set to {delete_after} seconds"), 
                seconds = delete_after, 
                goldy = goldy
            )

        return message
        """