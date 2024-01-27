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

    from ....goldy import Goldy

import asyncio
from devgoldyutils import LoggerAdapter

from ...message import Message
from .wrapper import PlatterWrapper
from ....logger import goldy_bot_logger

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
        hidden: bool = False, 
        **kwargs
    ) -> Message:
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

        if hidden: # shows the message only to the user
            payload["flags"] = 1 << 6

        payload.update(kwargs)

        message_data: MessageData = None

        # Callback message.
        # ------------------
        if self._interaction_responded is False:

            await self.goldy.low_level.send_interaction_callback(
                interaction_id = self.data["id"],
                interaction_token = self.data["token"],
                payload = payload,
                files = files
            )

            self._interaction_responded = True

            # Get and return message data of original interaction response. 
            message_data = await self.goldy.low_level.get_interaction_message(self.data["token"])

            self.logger.debug("Interaction callback message was sent.")

        # Follow up message.
        # -------------------
        # Is sent when you want to respond again after sending the original response to an interaction command.
        else:
            message_data = await self.goldy.low_level.send_interaction_follow_up(
                interaction_token = self.data["token"],
                payload = payload,
                files = files
            )

            self.logger.debug("Interaction follow up message was sent.")

        message = Message(message_data, self.goldy)

        if delete_after is not None:
            loop = asyncio.get_event_loop()

            async def delete_after_task():
                await asyncio.sleep(delete_after)
                await message.delete(
                    f"Automatic deletion set for {delete_after} seconds by 'delete_after' argument."
                )

            loop.create_task(delete_after_task())

        return message