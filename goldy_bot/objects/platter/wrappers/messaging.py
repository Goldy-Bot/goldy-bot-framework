from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from typing import Optional, List, Dict, NoReturn

    from discord_typings import (
        MessageData, 
        ActionRowData, 
        InteractionMessageCallbackData
    )

    from GoldyBot import Recipe

    from ....helpers import File

    from ....typings.objects import PlatterSelfT

import asyncio
from devgoldyutils import LoggerAdapter

from ....helpers import Embed
from ...message import Message
from ....colours import Colours
from ....logger import goldy_bot_logger
from ....errors import FrontEndError

__all__ = (
    "MessagingWrapper",
)

logger = LoggerAdapter(goldy_bot_logger, prefix = "MessagingWrapper")

class MessagingWrapper():
    def __init__(self) -> None:
        self._interaction_responded = False

        super().__init__()

    def error(
        self, 
        message: str, 
        title: str = "🧡 An Error Occurred!", 
        colour: Colours = Colours.AKI_ORANGE, 
        embed: Optional[Embed] = None
    ) -> NoReturn:
        """Raises a frond end error to the user."""

        if embed is None:
            embed = Embed(
                title = title,
                description = message,
                colour = colour
            )

        raise FrontEndError(embed, message, logger)

    async def wait(self: PlatterSelfT[Self]) -> None:
        """Informs Discord that this response will take longer than usual and it should wait."""

        if self._interaction_responded:
            logger.exception(
                "You cannot wait/defer an interaction response after it's already been responded!"
            )

            return None

        await self.goldy.low_level.wait(
            interaction_id = self.data["id"], interaction_token = self.data["token"]
        )

        self._interaction_responded = True

    async def send_message(
        self: PlatterSelfT[Self], 
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
            payload["embeds"] = [embed.data for embed in embeds]

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

        if hidden: # shows the message only to the user or deletes it after 5 seconds.

            if self._interaction_responded:
                delete_after = 5 if delete_after is None else delete_after
            else:
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

            logger.debug("Interaction callback message was sent.")

        # Follow up message.
        # -------------------
        # Is sent when you want to respond again after sending the original response to an interaction command.
        else:
            message_data = await self.goldy.low_level.send_interaction_follow_up(
                interaction_token = self.data["token"],
                payload = payload,
                files = files
            )

            logger.debug("Interaction follow up message was sent.")

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