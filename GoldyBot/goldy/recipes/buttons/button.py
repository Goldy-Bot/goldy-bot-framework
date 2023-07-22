from __future__ import annotations

import os
from enum import Enum
from typing import overload, Literal
from discord_typings import ButtonComponentData

from .. import Recipe, RECIPE_CALLBACK

class ButtonStyle(Enum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5

    BLURPLE = PRIMARY
    GREY = SECONDARY
    GREEN = SUCCESS
    RED = DANGER

class Button(Recipe):
    """
    A class used to create a slash command button.

    ---------------

    ⭐ Example:
    -------------
    This is how you use a button in goldy bot::

        @GoldyBot.command(
            description = "Have you ever wanted to 💣nuke a city? WELL FUCK IT, NOW YOU CAN!", 
            slash_options = {
                "city": SlashOption(
                    description = "The 🏢 city you would like to 💣nuke!"
                )
            }
        )
        async def nuke(self, platter: GoldyBot.GoldPlatter, city: str):

            await platter.send_message(
                f"Are you sure you would like to nuke **{city}**?",
                recipes = [
                    Button(ButtonStyle.GREEN, label="Yes", callback = self.nuke_city, city = city),
                    Button(ButtonStyle.RED, label="No", callback = lambda x: x.send_message("👨‍🦱 Alright we're holding off captain."))
                ]
            )

        
        async def nuke_city(self, platter: GoldyBot.GoldPlatter, city: str):
            casualties = random.randint(800, 10000)

            await platter.send_message(
                f"> 💣 You nuked {city}, there was {casualties} casualties.",
                reply = True
            )

    """
    @overload
    def __init__(
        self, 
        style: ButtonStyle | int, 
        label: str, 
        callback: RECIPE_CALLBACK, 
        emoji: str = None, 
        author_only: bool = True, 
        custom_id: str = None, 
        **callback_args: dict
    ) -> ButtonComponentData:
        ...

    @overload
    def __init__(
        self, 
        style: Literal[ButtonStyle.LINK, 5], 
        label: str, 
        url: str, 
        emoji: str = None, 
        author_only: bool = True, 
    ) -> ButtonComponentData:
        ...

    def __init__(
        self, 
        style: ButtonStyle | int, 
        label: str, 
        custom_id: str = None, 
        url: str = None, 
        emoji: str = None, 
        author_only: bool = True, 
        callback: RECIPE_CALLBACK = None, 
        **callback_args: dict
    ) -> ButtonComponentData:
        """
        Creates a discord button to use in action rows. 😋

        https://discord.com/developers/docs/interactions/message-components#buttons
        """
        if url is None and callback is None:
            raise TypeError(
                "Button class cannot have both url and callback set to None. Take a closer look at the arguments please."
            )

        data: ButtonComponentData = {}

        if isinstance(style, ButtonStyle):
            style = style.value

        if custom_id is None:
            custom_id = os.urandom(16).hex()

        data["type"] = 2 # ID type for button.
        data["style"] = style
        data["label"] = label

        if emoji is not None:
            # I don't personally use emojis any other way so for now I'll implement it like this. 
            # We may have an Emoji creator class in the future to improve things.
            data["emoji"] = {
                "id": None,
                "name": f"{emoji}"
            }

        if style == ButtonStyle.LINK.value:
            data["url"] = url
        else:
            data["custom_id"] = custom_id

        super().__init__(
            data = data, 
            name = data["label"],
            callback = callback,
            author_only = author_only, 
            **callback_args
        )

        if not style == ButtonStyle.LINK.value:
            self.register(custom_id)